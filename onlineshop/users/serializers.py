from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Order, DeliveryAddress, OrderItem
from shop.models import Products
from django.core.exceptions import ObjectDoesNotExist

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
        fields = ('id', 'phone_number', 'address', 'email', 'city', 'birth_date', 'avatar', 'user')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user

        # Проверка уникальности имени пользователя
        username = user_data.get('username', None)
        if username and username != user.username:
            if User.objects.filter(username=username).exists():
                raise serializers.ValidationError({"user": {"username": ["Пользователь с таким именем уже существует."]}})

        # Обновление полей пользователя
        for attr, value in user_data.items():
            if attr == 'password':
                if value:  # Обновляем пароль только если он не пустой
                    user.set_password(value)
            else:
                setattr(user, attr, value)
        user.save()

        # Обновление остальных полей профиля
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
        read_only_fields = ('id',) 

    def create(self, validated_data):
        product = Products.objects.create(**validated_data)
        return product

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)  # Читаем только имя продукта

    class Meta:
        model = OrderItem
        fields = ('id', 'product_name', 'quantity', 'price')

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User .objects.all())
    delivery_address = DeliveryAddressSerializer(allow_null=True)
    order_items = serializers.SerializerMethodField()  

    class Meta:
        model = Order
        fields = ('id', 'user', 'order_date', 'delivery_address', 'order_items',  'delivery_type', 'status', 'ready_at')
        read_only_fields = ('id', 'order_date')

    def get_order_items(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def create(self, validated_data):
        items_data = validated_data.pop('items', []) 
        delivery_address_data = validated_data.pop('delivery_address', None)
        user = validated_data.get('user') 

        if delivery_address_data:
            delivery_address = DeliveryAddress.objects.create(user=user, **delivery_address_data)
            validated_data['delivery_address'] = delivery_address

        total = 0
        order = Order(**validated_data)
        for item_data in items_data:
            try:
                product = Products.objects.get(pk=item_data['product'])
                item_total = product.price * item_data['quantity']
                total += item_total
                OrderItem.objects.create(order=order, product=product, **item_data)
            except Products.DoesNotExist:
                raise serializers.ValidationError("Такого продукта не существует.")

        order.total = total
        order.save() 

        return order


    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        delivery_address_data = validated_data.pop('delivery_address', None)

        # Обновление адреса доставки
        if delivery_address_data:
            for attr, value in delivery_address_data.items():
                setattr(instance.delivery_address, attr, value)
            instance.delivery_address.save()

        # Обновление полей заказа
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновление элементов заказа
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                try:
                    product = Products.objects.get(pk=item_data['product'])
                    OrderItem.objects.create(order=instance, product=product, **item_data)
                except ObjectDoesNotExist:
                    raise serializers.ValidationError("Такого продукта не существует.")

        return instance
