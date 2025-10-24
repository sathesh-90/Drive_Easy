from django.contrib import admin
from .models import Car, Booking, Maintenance, Driver, Customer



@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    pass


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user','phone', 'aadhar_number', 'license_number']


from django.contrib import admin
from .models import Driver, Car, Booking

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ['name',  'phone']
    search_fields = ['name','phone']

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['category', 'ac_type']
    list_filter = ['ac_type']
    search_fields = ['category', ]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'car', 'start_datetime']
    search_fields = ['customer__username', 'car__category']
    readonly_fields = ['created_at']
