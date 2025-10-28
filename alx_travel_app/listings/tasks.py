from celery import shared_task
from django.core.mail import send_mail
from .models import Bookings

@shared_task
def send_confirmation_email_task(booking_id):
    """Sends a confirmation email for a successfully paid booking."""
    try:
        booking = Bookings.objects.get(id=booking_id)
        
        # 1. Format the email content
        subject = f"Your Booking Confirmation for {booking.Listing.title}"
        message = (
            f"Dear {booking.guest.username},\n\n"
            f"Your booking has been successfully paid and confirmed!\n"
            f"Details: {booking.Listing.title}, Check-in: {booking.check_in_date}"
        )
        
        # 2. Send the email using Django's function
        send_mail(
            subject,
            message,
            'noreply@alxtravel.com', # From email
            [booking.guest.email], # To email
            fail_silently=False,
        )
        return "Email sent successfully"
        
    except Bookings.DoesNotExist:
        # Important: Log this error if a non-existent ID is passed
        print(f"Booking {booking_id} not found for email task.") 
        return "Booking not found"
