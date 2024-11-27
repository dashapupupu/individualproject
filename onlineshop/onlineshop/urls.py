from django.contrib import admin
from django.urls import path
from django.urls import *
from shop import views





urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('about/', views.about),
    path('contact/', views.contact),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/', views.cart, name='cart'),


]

from django.conf import settings
from django.conf.urls.static import static



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)