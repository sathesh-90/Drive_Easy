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
from django.contrib.auth.models import User
from .models import Customer

class EditProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Customer
        fields = ['phone', 'address', 'aadhar_number', 'license_number', 'profile_pic']

    def save(self, commit=True):
        customer = super().save(commit=False)
        user = customer.user

        # Update User fields
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')

        if self.cleaned_data.get('password'):
            user.set_password(self.cleaned_data.get('password'))

        if commit:
            user.save()
            customer.save()
        return customer





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

