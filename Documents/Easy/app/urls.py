# app/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('cars/', views.cars, name='cars'),
    path('about/', views.about, name='about'),
    path('booking/', views.booking_view, name='booking'),
    path("booked-cars/", views.booked_cars_view, name="booked_cars"),
    path("return-cars/", views.return_cars_view, name="return_cars"),

    # Distance calculator
    path('distance-calculator/', views.distance_calculator, name='distance_calculator'),
    path('calculate-distance/', views.calculate_distance, name='calculate_distance'),

    # Authentication (custom views)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('drivers/', views.drivers_view, name='drivers'),


     # Staff URLs
     path('staff/booked_cars/', views.staff_booked_cars_view, name='staff_booked_cars'),
     path('staff/returned_cars/<int:booking_id>/', views.staff_returned_cars_view, name='staff_returned_cars'),
     path('staff/returned_cars/', views.staff_returned_cars_list_view, name='staff_returned_cars_list'),
     path('staff/returned_cars/mark/<int:booking_id>/', views.staff_returned_cars_mark, name='staff_returned_cars_mark'),



    path('password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='app/password_reset.html'), 
         name='password_reset'),
         
    path('password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), 
         name='password_reset_done'),
         
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html'), 
         name='password_reset_confirm'),
         
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), 
         name='password_reset_complete'),


path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

]
