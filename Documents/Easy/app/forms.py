# app/forms.py
from django import forms
from .models import Booking
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['pickup_location', 'drop_location', 'start_datetime','expected_return_datetime',  'night_halt']

        widgets = {
            "start_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "expected_return_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }

from django import forms
from .models import Driver

class DriverForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = [
            'name', 'image', 'license_number', 'aadhar_number', 
            'phone', 'email', 'address', 'experience'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter driver full name'
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter license number'
            }),
            'aadhar_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Aadhar number'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3
            }),
            'experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Years of experience'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }

