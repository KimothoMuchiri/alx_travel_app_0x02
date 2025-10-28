from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator 

class Listing(models.Model):
    #property name
    title = models.CharField(max_length=255)

    # description of the place
    description = models.TextField()

    # The price per night
    price_per_night = models.DecimalField(max_digits = 10, decimal_places = 2)

    #The location
    location = models.CharField(max_length= 100)

    # When the listing was created
    created_at = models.DateTimeField(auto_now_add = True) 

class Bookings(models.Model):
    Listing = models.ForeignKey(
        'Listing',
        on_delete = models.CASCADE,
        related_name = 'bookings' # allows accessing bookings from a Listing instance
    )

    # (Many bookings to One User)
    guest = models.ForeignKey(User, on_delete = models.CASCADE)

    check_in_date = models.DateField()
    check_out_date = models.DateField()

    # Calculate the total price based n price_per_night
    total_price = models.DecimalField(max_digits = 10, decimal_places = 2)

    # field to track booking status
    is_paid = models.BooleanField(default= False)
    
    class Meta:
        # Prevents one guest from booking the same listing on the same start date twice
        unique_together = ('Listing', 'check_in_date', 'guest')

    def __str_(self):
        return f"Booking for {self.listing.title} by {self.guest.username}"

class Review(models.Model):
    # Links the review t the listing
    Listing = models.ForeignKey(
        'Listing',
        on_delete = models.CASCADE,
        related_name = 'reviews' # allows accessing reviews from a Listing instance
    )

    # (Many reviews to One User)
    author = models.ForeignKey(User, on_delete= models.SET_NULL, null = True)

    rating = models.PositiveSmallIntegerField(
        help_text = "Rating must be between 1 and 5.",
        validators = [MinValueValidator(1), MaxValueValidator(5)]
    )

    comment = models.TextField()
    created_at = models.DateField(auto_now_add = True)

    def __str__(self):
        return f"Review for {self.Listing.title}: {self.rating} stars"

# Payments_Model
# Payments status choices
PAYMENT_STATUS_CHOICES = (
    ('P','Pending'),
    ('C', 'Completed'),
    ('F', 'Failed'),
    ('E', 'Expired'),
)
class Payment(models.Model):
    # A reference to the original booking
    booking = models.ForeignKey(
        'Bookings',
        on_delete = models.CASCADE,
        related_name='payments' # Allows you to access all payments for a booking
    )

    #unique transaction reference sent to Chapa
    trans_ref = models.CharField(max_length = 100, unique = True)

    amount = models.DecimalField(max_digits = 10, decimal_places = 2)

    status = models.CharField(
        max_length = 1,
        choices = PAYMENT_STATUS_CHOICES
    )

    # stre the chapa response in  a jason field
    chapa_response = models.JSONField(default=dict, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)

    def __str__(self):
        return f"Payment for {self.booking_ref} - Status: {self.get_status_display()}"







