from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Order, DeliveryAddress, OrderItem
from shop.models import Products


from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}} 

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)
    class Meta:
        model = UserProfile
        fields = ('id','phone_number', 'address', 'email', 'city', 'birth_date', 'avatar', 'user')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        for attr, value in user_data.items():
            if attr != 'password': 
                setattr(user, attr, value)
        user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ('id', 'address', 'city')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ('id', 'name', 'price', 'discount', 'description', 'categories', 'image', 'proizvoditel')
        read_only_fields = ('id',)  # Поле id будет только для чтения

    def create(self, validated_data):
        # Создание нового продукта
        product = Products.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):
        # Обновление существующего продукта
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)  # Читаем только имя продукта

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User .objects.all())
    delivery_address = DeliveryAddressSerializer(allow_null=True)
    order_items = OrderItemSerializer(many=True, source='items')  # Исправлено на 'items'

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_date', 'delivery_address', 'order_items', 'delivery_type', 'total', 'status', 'ready_at')
        read_only_fields = ('id', 'order_date')

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        delivery_address_data = validated_data.pop('delivery_address', None)

        if delivery_address_data:
            delivery_address = DeliveryAddress.objects.create(**delivery_address_data)
            validated_data['delivery_address'] = delivery_address

        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        delivery_address_data = validated_data.pop('delivery_address', None)

        if delivery_address_data:
            for attr, value in delivery_address_data.items():
                setattr(instance.delivery_address, attr, value)
            instance.delivery_address.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        return instance
