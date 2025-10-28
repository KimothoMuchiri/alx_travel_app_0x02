from django.contrib import admin
from .models import Listing, Bookings, Review # Import your models

# Register your models here
admin.site.register(Listing)
admin.site.register(Bookings)
admin.site.register(Review)
