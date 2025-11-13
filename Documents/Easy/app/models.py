from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Car(models.Model):
    CATEGORY_CHOICES = [
        ('Ambassador', 'Ambassador'),
        ('Tata Sumo', 'Tata Sumo'),
        ('Maruti Omni', 'Maruti Omni'),
        ('Maruti Esteem', 'Maruti Esteem'),
        ('Mahindra Armada', 'Mahindra Armada'),
    ]
    AC_CHOICES = [('AC', 'AC'), ('Non-AC', 'Non-AC')]
    STATUS_CHOICES = [('available', 'Available'),  ('repair', 'Repair')]
    Fuel_con = [('petrol', 'Petrol'),  ('diesel', 'Diesel'),('gas','Gas'),('electric','Electric')]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    ac_type = models.CharField(max_length=10, choices=AC_CHOICES)
    total_cars=models.IntegerField(default=1)
    registration_number = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='cars/')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    price_per_hour = models.FloatField(default=0)
    price_per_km = models.FloatField(default=0)

    fuel_consumption = models.CharField(max_length=15, choices=Fuel_con, default='diesel')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
        # New fields for return flow
    is_returned = models.BooleanField(default=False)
    pending_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    damage_reported = models.BooleanField(default=False)
    damage_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.category} ({self.registration_number})"

# Driver connection with car (if not using DriverProfile)
class Driver(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('ASSIGNED', 'Assigned'),
        ('ON_LEAVE', 'On Leave'),
    ]
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    image = models.ImageField(upload_to='drivers/', blank=True, null=True)
    license_number = models.CharField(max_length=20, unique=True)
    aadhar_number = models.CharField(max_length=12, unique=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    experience = models.IntegerField(default=0, help_text="Years of experience")
    
    def __str__(self):
        return self.name
    
from django.db import models
from django.contrib.auth import get_user_model

class Customer(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile"
        # Remove null=True, blank=True
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    aadhar_number = models.CharField(max_length=12, unique=True, blank=True, null=True)
    license_number = models.CharField(max_length=20, blank=True, null=True)
    profile_pic = models.ImageField(upload_to="profile_pics/", default="default_avatar.png")
    def __str__(self):
        return self.user.username

from django.contrib.auth.models import User  # or your CustomUser if you have one
from decimal import Decimal

class Booking(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    expected_return_datetime = models.DateTimeField()
    actual_return_datetime = models.DateTimeField(null=True, blank=True)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    start_km_reading = models.IntegerField(null=True, blank=True)
    end_km_reading = models.IntegerField(null=True, blank=True)
    night_halt = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pending_payment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(default=timezone.now)
    pickup_location = models.CharField(max_length=100, null=True, blank=True)
    drop_location = models.CharField(max_length=100, null=True, blank=True)
    distance_km = models.FloatField(null=True, blank=True)
    is_returned = models.BooleanField(default=False)
    returned_at = models.DateTimeField(null=True, blank=True)
    damage_fee = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    damage_reported = models.BooleanField(default=False)
    kms_to_destination = models.PositiveIntegerField(default=0)
    hours_used = models.IntegerField(default=4)
    DRIVE_CHOICES = [
        ('self_drive', 'Self Drive'),
        ('with_driver', 'With Driver')
    ]
    drive_type = models.CharField(
        max_length=20,
        choices=DRIVE_CHOICES,
        default='self_drive'  # <-- default value for existing rows
    )
    def __str__(self):
        return f"Booking by {self.customer.username} → {self.car}"
    



    # Optional: method to calculate distance (call this from a view or form)
    def calculate_distance(self, api_key):
        import requests
        endpoint = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": self.pickup_location,
            "destination": self.drop_location,
            "key": api_key,
        }
        response = requests.get(endpoint, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                distance_meters = data['routes'][0]['legs'][0]['distance']['value']
                self.distance_km = distance_meters / 1000.0
                self.save()
                return self.distance_km
        return None

class Maintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return f"{self.car} - {self.date}"
    
