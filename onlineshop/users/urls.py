from django.urls import path
from .views import register, user_login, profile, edit_profile, add_delivery_address, delete_delivery_address, logout_view, request_password_reset, verify_code,reset_password
from django.contrib.auth import views as auth_views
from .views import UserProfileViewSet, ProductViewSet, LogoutView, OrderViewSet
# from .views import user_profile_list, user_profile_detail
from users import views
from rest_framework.urlpatterns import format_suffix_patterns
from .views import LoginView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'llogin', LoginView, basename='llogin')

# router.register(r'pproducts', ProductListCreateView)
router.register(r'oorders', OrderViewSet)
router.register(r'uusers', UserProfileViewSet, basename='uusers')
router.register(r'pproducts', ProductViewSet, basename='pproduct')
router.register(r'llogout', LogoutView, basename='llogout')




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
    # path('orders/', views.OrderListCreateView.as_view(), name='order-list-create'), 
    # path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'), 
    # path('products/', ProductListCreateView.as_view(), name='product-list-create'),
    # path('products/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('', include(router.urls))

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
    
  
    
    




