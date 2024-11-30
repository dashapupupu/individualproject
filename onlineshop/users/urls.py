from django.urls import path
from .views import register, user_login, profile, edit_profile, add_delivery_address, delete_delivery_address, logout_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('add-delivery-address/', add_delivery_address, name='add_delivery_address'),
    path('delete-delivery-address/<int:address_id>/', delete_delivery_address, name='delete_delivery_address'),
    path('logout/', logout_view, name='logout'),




]