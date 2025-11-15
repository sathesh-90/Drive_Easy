# views.py
import logging
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.db.models import Q, Sum

from .forms import BookingForm
from .models import Booking, Car, Customer, Driver

logger = logging.getLogger(__name__)
User = get_user_model()


# -----------------------
# Basic pages
# -----------------------
def index(request):
    return render(request, "app/index.html")


def about(request):
    return render(request, "app/about.html")


def cars(request):
    query = request.GET.get("q", "").strip()
    if query:
        cars_qs = Car.objects.filter(
            Q(category__icontains=query)
            | Q(ac_type__icontains=query)
            | Q(fuel_consumption__icontains=query)
        )
    else:
        cars_qs = Car.objects.all()
    return render(request, "app/cars.html", {"cars": cars_qs, "query": query})


# -----------------------
# Booking flow
# -----------------------
@login_required
def booking_view(request):
    """
    Create a booking for a given car. Expects car_id as GET or POST param.
    Calculates amounts and saves booking. Ensures customer record exists.
    """
    car_id = request.GET.get("car_id") or request.POST.get("car_id")
    if not car_id:
        messages.error(request, "No car specified.")
        return redirect("cars")

    car = get_object_or_404(Car, id=car_id)
    customer_profile, _ = Customer.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.car = car
            booking.customer = request.user

            # Read dynamic fields (with safe defaults)
            try:
                kms_to_destination = int(request.POST.get("kms_to_destination") or request.POST.get("km_to_destination") or 0)
            except (ValueError, TypeError):
                kms_to_destination = 0

            try:
                hours_used = int(request.POST.get("hours_used") or 4)
            except (ValueError, TypeError):
                hours_used = 4
            hours_used = max(hours_used, 4)

            drive_type = request.POST.get("drive_type", "self_drive")

            # For self-drive store aadhar/license in Customer
            if drive_type == "self_drive":
                aadhaar_number = request.POST.get("aadhaar_number", "").strip()
                license_number = request.POST.get("license_number", "").strip()
                if not aadhaar_number or not license_number:
                    messages.error(request, "Aadhaar and License required for self-drive.")
                    return render(request, "app/booking.html", {"form": form, "car": car, "customer": customer_profile})
                customer_profile.aadhar_number = aadhaar_number
                customer_profile.license_number = license_number
                customer_profile.save()

            # Calculate fares (use Car fields)
            per_hour_charge = Decimal(str(car.price_per_hour or 0))
            per_km_charge = Decimal(str(car.price_per_km or 0))
            hourly_amount = per_hour_charge * Decimal(hours_used)
            km_amount = per_km_charge * Decimal(kms_to_destination)
            minimum_base = per_hour_charge * Decimal(4)
            total_amount = max(hourly_amount, km_amount, minimum_base)

            if drive_type == "with_driver":
                total_amount += Decimal("500.00")

            advance_payment = (total_amount * Decimal("0.20")).quantize(Decimal("0.01"))
            pending_payment = (total_amount - advance_payment).quantize(Decimal("0.01"))

            # Save booking fields (ensure decimals are Decimal)
            booking.kms_to_destination = kms_to_destination
            booking.hours_used = hours_used
            booking.total_amount = total_amount.quantize(Decimal("0.01"))
            booking.advance_payment = advance_payment
            booking.pending_payment = pending_payment
            booking.drive_type = drive_type
            booking.start_km_reading = booking.start_km_reading or 0
            booking.save()

            # Decrement fleet availability
            if car.total_cars and car.total_cars > 0:
                car.total_cars -= 1
                car.save()

            messages.success(request, f"Booking successful! Pending Amount: ₹{pending_payment:.2f}")
            return redirect("booked_cars")
    else:
        form = BookingForm()

    return render(request, "app/booking.html", {"form": form, "car": car, "customer": customer_profile})


# -----------------------
# Authentication
# -----------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        profile_pic = request.FILES.get("profile_pic")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, "app/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, "app/register.html")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, "app/register.html")

        user = User.objects.create_user(username=username, email=email, password=password1)
        # create customer profile with optional profile pic
        Customer.objects.get_or_create(user=user, defaults={"profile_pic": profile_pic})
        login(request, user)
        return redirect("index")

    return render(request, "app/register.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "app/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile_view(request):
    """View and update basic user profile (first_name, last_name, email)."""
    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", "").strip()
        user.last_name = request.POST.get("last_name", "").strip()
        user.email = request.POST.get("email", "").strip()

        if user.first_name and user.email:
            try:
                user.save()
                messages.success(request, "Profile updated successfully!")
            except Exception:
                messages.error(request, "Error updating profile. Please try again.")
        else:
            messages.error(request, "Please fill in all required fields.")

    # Ensure a customer profile exists
    Customer.objects.get_or_create(user=request.user)
    return render(request, "app/profile.html")


# -----------------------
# Distance / Maps helpers
# -----------------------
def distance_calculator(request):
    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    if not api_key:
        logger.error("Google Maps API key not found in settings")
    else:
        logger.debug("Google Maps API key present")
    return render(request, "app/distance_calculator.html", {"google_maps_api_key": api_key})


def calculate_distance(request):
    """
    AJAX endpoint to call Google Distance Matrix and return estimated fare.
    Expects POST with 'origin' and 'destination'.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"})

    origin = request.POST.get("origin", "").strip()
    destination = request.POST.get("destination", "").strip()

    if not origin or not destination:
        return JsonResponse({"error": "Both origin and destination are required"})

    api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)
    if not api_key:
        logger.error("Google Maps API key not configured")
        return JsonResponse({"error": "Google Maps API key not configured. Please check your settings."})

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {"origins": origin, "destinations": destination, "units": "metric", "key": api_key}

    try:
        resp = requests.get(url, params=params, timeout=10)
        logger.debug("Google API response: %s", resp.text)
        if resp.status_code != 200:
            return JsonResponse({"error": f"HTTP Error: {resp.status_code}"})

        data = resp.json()
        if data.get("status") != "OK":
            err = data.get("status", "UNKNOWN_ERROR")
            return JsonResponse({"error": f"API Error: {err}", "details": data.get("error_message")})

        element = data["rows"][0]["elements"][0]
        if element.get("status") != "OK":
            return JsonResponse({"error": f"Route calculation failed: {element.get('status')}"})

        distance_text = element["distance"]["text"]
        duration_text = element["duration"]["text"]
        distance_value = element["distance"]["value"]  # meters
        duration_value = element["duration"]["value"]  # seconds

        fare_per_km = Decimal("12.50")
        fare_per_hour = Decimal("200")

        distance_km = Decimal(distance_value) / Decimal("1000")
        duration_hours = Decimal(duration_value) / Decimal("3600")

        distance_fare = (distance_km * fare_per_km).quantize(Decimal("0.01"))
        time_fare = (duration_hours * fare_per_hour).quantize(Decimal("0.01"))
        estimated_fare = max(distance_fare, time_fare)

        return JsonResponse(
            {
                "success": True,
                "distance": distance_text,
                "duration": duration_text,
                "distance_km": float(distance_km),
                "duration_hours": float(duration_hours),
                "distance_fare": float(distance_fare),
                "time_fare": float(time_fare),
                "estimated_fare": float(estimated_fare),
                "origin": origin,
                "destination": destination,
            }
        )
    except requests.exceptions.Timeout:
        logger.exception("Maps API timeout")
        return JsonResponse({"error": "Request timeout. Please try again."})
    except requests.exceptions.RequestException as e:
        logger.exception("Maps API request exception")
        return JsonResponse({"error": f"Request error: {str(e)}"})
    except (KeyError, ValueError) as e:
        logger.exception("Maps API parse error")
        return JsonResponse({"error": "Invalid response from Google API"})


# -----------------------
# Booked / Returned lists
# -----------------------
@login_required
def booked_cars_view(request):
    """List bookings: staff sees all pending bookings; customers see their own."""
    if request.user.is_staff:
        total_cars_booked = Booking.objects.filter(is_returned=False).count()
        r_total_cars_booked = Booking.objects.filter(is_returned=True).count()
        bookings = Booking.objects.filter(is_returned=False).order_by("-start_datetime")
    else:
        total_cars_booked = Booking.objects.filter(customer=request.user, is_returned=False).count()
        r_total_cars_booked = Booking.objects.filter(customer=request.user, is_returned=True).count()
        bookings = Booking.objects.filter(customer=request.user).order_by("-start_datetime")

    context = {
        "bookings": bookings,
        "total_cars_booked": total_cars_booked,
        "r_total_cars_booked": r_total_cars_booked,
    }
    return render(request, "app/booked_cars.html", context)


@login_required
def return_cars_view(request):
    """Staff view of returned cars (for staff dashboard)."""
    if not request.user.is_staff:
        return redirect("index")
    bookings = Booking.objects.filter(is_returned=True).order_by("-returned_at")
    returned_cars = bookings.count()
    return render(request, "app/return_cars.html", {"bookings": bookings, "returned_cars": returned_cars})


@login_required
def returns_list_view(request):
    """Customer view: their returned bookings."""
    bookings = Booking.objects.filter(customer=request.user, is_returned=True).order_by("-returned_at")
    return render(request, "app/customer_returned_cars.html", {"bookings": bookings})


# -----------------------
# Staff actions (mark returned)
# -----------------------
@user_passes_test(lambda u: u.is_staff)
def staff_returned_cars_mark(request, booking_id):
    """
    POST handler to mark a booking returned and optionally record damage + fee.
    Form fields expected:
      - damage_reported : checkbox "on" when present
      - damage_fee : numeric string (optional)
    """
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        damage_flag = request.POST.get("damage_reported")
        damage_fee_raw = (request.POST.get("damage_fee") or "").strip()

        damage_reported = bool(damage_flag)
        damage_fee = Decimal("0.00")
        if damage_fee_raw:
            try:
                damage_fee = Decimal(damage_fee_raw)
                if damage_fee < 0:
                    damage_fee = Decimal("0.00")
            except (InvalidOperation, ValueError):
                damage_fee = Decimal("0.00")

        # Update booking's damage fields
        booking.damage_reported = damage_reported
        booking.damage_fee = damage_fee

        # If booking not already returned, increment fleet and set returned flags/time
        if not booking.is_returned:
            car = booking.car
            car.total_cars = (car.total_cars or 0) + 1
            car.save()
            booking.is_returned = True
            booking.returned_at = timezone.now()

        # Recalculate totals:
        # We assume booking.total_amount previously did NOT include damage_fee.
        base_total = booking.total_amount or Decimal("0.00")
        booking.total_amount = (base_total + damage_fee).quantize(Decimal("0.01"))
        booking.pending_payment = (booking.total_amount - (booking.advance_payment or Decimal("0.00"))).quantize(
            Decimal("0.01")
        )

        booking.save()
        messages.success(request, "Booking updated and marked returned.")

    return redirect("staff_returned_cars_list")


@staff_member_required
def staff_returned_cars_view(request, booking_id):
    """
    Quick mark-return (no damage info). If damage was already set earlier, respects it.
    """
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.is_returned:
        messages.info(request, f"The booking for {booking.car.category} is already returned.")
        return redirect("staff_booked_cars")

    booking.is_returned = True
    booking.returned_at = timezone.now()

    car = booking.car
    car.total_cars = (car.total_cars or 0) + 1
    car.save()

    damage_fee = booking.damage_fee or Decimal("0.00")
    if booking.damage_reported and damage_fee > 0:
        booking.total_amount = (booking.total_amount or Decimal("0.00")) + damage_fee

    booking.pending_payment = (booking.total_amount or Decimal("0.00")) - (booking.advance_payment or Decimal("0.00"))
    booking.save()
    messages.success(request, "Booking marked returned.")
    return redirect("staff_booked_cars")


@staff_member_required
def staff_booked_cars_view(request):
    bookings = Booking.objects.filter(is_returned=False).order_by("-start_datetime")
    total_cars_booked = bookings.count()
    r_total_cars_booked = Booking.objects.filter(is_returned=True).count()
    return render(
        request,
        "app/staff_booked_cars.html",
        {"bookings": bookings, "total_cars_booked": total_cars_booked, "r_total_cars_booked": r_total_cars_booked},
    )


@staff_member_required
def staff_returned_cars_list_view(request):
    bookings = Booking.objects.filter(is_returned=True).order_by("-returned_at")
    return render(request, "app/staff_returned_cars_list.html", {"bookings": bookings})


# -----------------------
# Drivers and admin
# -----------------------
@login_required
def drivers_view(request):
    drivers = Driver.objects.all()
    total_drivers = drivers.count()
    return render(request, "app/drivers.html", {"drivers": drivers, "total_drivers": total_drivers})


@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect("index")

    total_bookings = Booking.objects.count()
    total_revenue = Booking.objects.aggregate(Sum("total_amount"))["total_amount__sum"] or Decimal("0.00")
    total_drivers = Driver.objects.count()
    total_cars = Car.objects.count()
    returned_cars = Booking.objects.filter(is_returned=True).count()
    pending_bookings = Booking.objects.filter(is_returned=False).count()

    context = {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "total_drivers": total_drivers,
        "total_cars": total_cars,
        "returned_cars": returned_cars,
        "pending_bookings": pending_bookings,
    }
    return render(request, "app/admin_dashboard.html", context)


def password_reset_done_custom(request):
    return render(request, "app/password_reset_done.html")
