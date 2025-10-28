from rest_framework import serializers
from .models import Listing, User, Review, Bookings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','email') # only expose the safe fields

class BookingSerializer(serializers.ModelSerializer):
    # READ-ONLY FIELD (For GET responses - to display full guest data)
    guest_details = UserSerializer(source='guest', read_only = True)

    # WRITABLE FIELD (For POST requests - to accept the guest ID)
    guest = serializers.PrimaryKeyRelatedField(queryset=User.objects.all()) 

    class Meta:
        model = Bookings
        # The 'listing' ForeignKey field is included because we need to know 
        # which listing is being booked (either by its ID or nested data).

        fields = ('id', 'Listing','guest','guest_details','check_in_date', 'check_out_date','total_price','is_paid')

class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source = 'author.username')

    class Meta:
        model = Review
        fields = ('id', 'Listing', 'author', 'rating', 'comment', 'created_at')

class ListingSerializer(serializers.ModelSerializer):
    """ 
    A user is viewing a single Listing on the website. 
    They want to see all the reviews and all the bookings associated 
    with that property right there on the page. You need to use the related_name 
    values—'reviews' and 'bookings'—to access that data
    """
    # Nest the ReviewSerializer and set many=True
    reviews = ReviewSerializer(many = True, read_only = True)
    # Nest the BokingsSerializer and set many = True
    bookings = BookingSerializer(many=True, read_only=True)

    class Meta:
        # which model
        model = Listing

        # Which fields from the model should be included in the API response?
        fields = ('id', 'title','description', 'price_per_night', 'location', 'reviews','bookings')

