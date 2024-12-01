from django.contrib import admin
from.models import Categories, Products, Proizvoditel
from users.models import OrderItem, Order

admin.site.register(Categories)
admin.site.register(Proizvoditel)
admin.site.register(Products)
admin.site.register(Order)
admin.site.register(OrderItem)

