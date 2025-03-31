from django.urls import path
from .views import register, user_login, profile, edit_profile, add_delivery_address, delete_delivery_address, logout_view, request_password_reset, verify_code,reset_password, LogoutView
from django.contrib.auth import views as auth_views
from .views import UserProfileView, UserProfileDetailView, ProductDetailView, ProductListCreateView
# from .views import user_profile_list, user_profile_detail
from users import views
from .views import ApiRoot
from rest_framework.urlpatterns import format_suffix_patterns
from .views import LoginView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'logun', LoginView, basename='logun')
router.register(r'logut', LogoutView, basename='logut')



urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('profile/', profile, name='profile'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('add-delivery-address/', add_delivery_address, name='add_delivery_address'),
    path('delete-delivery-address/<int:address_id>/', delete_delivery_address, name='delete_delivery_address'),
    path('logout/', logout_view, name='logout'),
    path('request-password-reset/', request_password_reset, name='request_password_reset'),
    path('verify-code/', verify_code, name='verify_code'),
    path('reset-password/', reset_password, name='reset_password'),
    path('users/', UserProfileView.as_view(), name='userprofile'),
    path('users/<int:pk>/', UserProfileDetailView.as_view(), name='userprofile-detail'),
    path('orders/', views.OrderListCreateView.as_view(), name='order-list-create'), 
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'), 
    path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('', ApiRoot.as_view(), name='api-root'),
    path('api/', include(router.urls))

    # path('users/', views.user_profile_list, name='userprofile'),
    # path('users/<int:pk>/', views.user_profile_detail, name='userprofile-detail'),

]


# urlpatterns = format_suffix_patterns(urlpatterns)


# from django.urls import path
# from .views import register, user_login, profile, edit_profile, add_delivery_address, delete_delivery_address, logout_view, request_password_reset, verify_code,reset_password
# from django.contrib.auth import views as auth_views
# from .views import UserProfileViewSet


# urlpatterns = [
#     path('register/', register, name='register'),
#     path('login/', user_login, name='login'),
#     path('profile/', profile, name='profile'),
#     path('edit-profile/', edit_profile, name='edit_profile'),
#     path('add-delivery-address/', add_delivery_address, name='add_delivery_address'),
#     path('delete-delivery-address/<int:address_id>/', delete_delivery_address, name='delete_delivery_address'),
#     path('logout/', logout_view, name='logout'),
#     path('request-password-reset/', request_password_reset, name='request_password_reset'),
#     path('verify-code/', verify_code, name='verify_code'),
#     path('reset-password/', reset_password, name='reset_password'),
#     path('users/', UserProfileViewSet.as_view({'get': 'list'}), name='userprofile'),
#     path('users/<int:pk>/', UserProfileViewSet.as_view({'get': 'retrieve'}), name='userprofile-detail'),
# ]
    
  
    
    




