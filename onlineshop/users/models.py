from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator
from shop.models import Products

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Телефонный номер должен быть введен в формате: '+999999999'. Допускается до 15 цифр.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, unique=True)
    address = models.TextField(blank=True)
    email = models.EmailField(null=True, blank=True, unique=True)  
    city = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Профиль пользователя: {self.user.username}"

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='delivery_addresses') 
    address = models.TextField()
    city = models.CharField(max_length=100)
    

    def __str__(self):
        return f"Адрес доставки пользователя {self.user.username}: {self.address}"
    

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_type = models.CharField(max_length=20, choices=[('courier', 'Доставка курьером'), ('pickup', 'Самовывоз')], default='courier')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Ожидание'), ('processing', 'Обработка'), ('ready', 'Готов'), ('delivered', 'Доставлен')], default='Магазин не существует вы олух')
    ready_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Заказ #{self.id} пользователя {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) 


    def __str__(self):
        return f"Товар {self.product} в заказе #{self.order.id}"
    




