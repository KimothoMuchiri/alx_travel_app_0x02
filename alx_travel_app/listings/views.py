import os
import uuid
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Bookings, Payment
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_confirmation_email_task

class ListingViewSet(viewsets.ModelViewSet):
    # queryset tells the mdel which objects it should work with
    queryset = Listing.objects.all()

    # serializer tells the viewset how to convert model data
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    # queryset tells the mdel which objects it should work with
    queryset = Bookings.objects.all()

    # serializer tells the viewset how to convert model data
    serializer_class = BookingSerializer

CHAPA_API_URL = "https://api.chapa.co/v1/transaction/initialize"

class InitiatePaymentView(APIView):
    def post(self, request, booking_id):
        try:
            booking = Bookings.objects.get(id=booking_id)
        except Bookings.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)

        # generate a unique transaction reference

        trans_ref = f"ALX-TRAVEL-{uuid.uuid4().hex[:15]}"

        #payment data paylad
        payload = {
            "amount" : str(booking.total_price),
            "currency": "ETB",
            "email": booking.guest.email,
            "first_name": booking.guest.first_name or "Guest",
            "last_name": booking.guest.last_name or "User",
            "trans_ref": trans_ref,
            # This is the API endpoint that Chapa will hit 
            "callback_url": f"{settings.BASE_URL}/api/payments/verify/{trans_ref}/",
            # This is where the user's browser redirects after payment
            "return_url": f"{settings.FRONTEND_URL}/payment-status/?trans_ref={trans_ref}",
        }

        # Call the Chapa API
        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(CHAPA_API_URL, json= payload, headers=headers),
        chapa_data = response.json()

        if response.status_code == 200 and chapa_data.get('status') == 'success':
            # 4. Create the initial 'Pending' payment record in your database
            Payment.objects.create(
                booking=booking,
                trans_ref=trans_ref,
                amount=booking.total_price,
                status='P', # Pending
                chapa_response=chapa_data
            )
            
            # 5. Return the crucial checkout URL to the frontend
            return Response({"checkout_url": chapa_data['data']['checkout_url']}, status=status.HTTP_200_OK)
        else:
            # Handle API call failures gracefully
            return Response({"error": "Chapa API initiation failed.", "details": chapa_data}, status=status.HTTP_400_BAD_REQUEST)


# Verififcation URL

CHAPA_VERIFY_URL = "https://api.chapa.co/v1/transaction/verify"

class VerifyPaymentView(APIView):
    def get(self, request, trans_ref):
        # look-up the payment record in the database
        try:
            payment = Payment.objects.get(trans_ref = trans_ref)
        except Payment.DoesNotExist:
            return Response({"error": "Invalid transaction reference."}, status=status.HTTP_404_NOT_FOUND)
        
        # prepare the verififcation request to chapa
        headrs = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
        }

        # the cmplete verification url
        verify_url = f"{CHAPA_VERIFY_URL/{trans_ref}}"

        # Call the Chapa API to verify the status
        response = requests.get(verify_url, headers=headers)
        chapa_verification_data = response.json()

        # Process Chapa's response and update your model
        if response.status_code == 200 and chapa_verification_data.get('status') == 'success':
            
            # **Crucial Check:** Confirm Chapa's data matches the records
            chapa_data_status = chapa_verification_data['data']['status']
            
            if chapa_data_status == 'success' and chapa_verification_data['data']['amount'] >= payment.amount:
                
                # Payment is successful! Update your local record.
                payment.status = 'C' # Completed
                payment.chapa_response = chapa_verification_data
                payment.save()
                
                # Mark the Booking as paid
                booking = payment.booking 
                booking.is_paid = True 
                booking.save()

                # Send the email in the background
                send_confirmation_email_task.delay(booking.id)
                
                return Response({"message": "Payment verified and completed.", "status": "Completed"}, status=status.HTTP_200_OK)
            
            elif chapa_data_status == 'failed':
                payment.status = 'F' # Failed
                payment.chapa_response = chapa_verification_data
                payment.save()
                return Response({"message": "Payment verified, but status is FAILED.", "status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Handle API errors or unexpected responses
        payment.status = 'F' # Default to failed if verification is ambiguous
        payment.save()
        return Response({"message": "Verification failed or API error occurred.", "status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)

