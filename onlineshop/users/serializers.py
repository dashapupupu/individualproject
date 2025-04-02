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
        extra_kwargs = {
            'password': {
                'write_only': True,
                'required': False
            },
            'username': {
                'required': False
            }
        }

    def validate_username(self, value):
        """Проверка уникальности username только при изменении"""
        if not value:
            return getattr(self.instance, 'username', '')
            
        if self.instance and value == self.instance.username:
            return value
            
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует.")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = UserProfile
        fields = ('id', 'phone_number', 'address', 'email', 'city',
                 'birth_date', 'avatar', 'user')
        extra_kwargs = {
            'phone_number': {'required': False},
            'address': {'required': False},
            'city': {'required': False},
            'birth_date': {'required': False},
            'avatar': {'required': False}
        }

    def create(self, validated_data):
        user_data = validated_data.pop('user', {})
        email = user_data.pop('email', None)
        
        # Создаем пользователя
        user = User.objects.create_user(
            username=user_data.get('username'),
            password=user_data.get('password'),
            email=email
        )
        
        # создание 
        profile = UserProfile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        email = user_data.pop('email', None)
        
        # Обнов профиль
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # обнов пользователя
        if user_data or email is not None:
            user = instance.user
            if email is not None:
                user.email = email
            if user_data:
                for attr, value in user_data.items():
                    if attr == 'password' and value:
                        user.set_password(value)
                    else:
                        setattr(user, attr, value)
            user.save()
        
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

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # инфо о продукте
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Products.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']
        read_only_fields = ['id', 'product', 'price']

from rest_framework import serializers
from .models import Order, OrderItem, DeliveryAddress, Products

from rest_framework import serializers
from .models import Order, OrderItem, Products, DeliveryAddress

from rest_framework import serializers
from .models import Order, OrderItem, Products, DeliveryAddress

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='items', read_only=True)
    products = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True,
        help_text="List of product dictionaries with 'id' and optional 'quantity'. Example: [{'id': 1, 'quantity': 2}]"
    )
    delivery_address = DeliveryAddressSerializer(
        allow_null=True,
        required=False
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_date', 'delivery_address', 
            'delivery_type', 'status', 'total', 'ready_at',
            'order_items', 'products'
        ]
        read_only_fields = ['id', 'user', 'order_date', 'status', 'total', 'order_items']

    def validate(self, data):
        products_data = data.get('products', [])
        if not products_data:
            raise serializers.ValidationError({"products": "Необходимо указать хотя бы один товар"})

        validated_products = []
        for idx, product_item in enumerate(products_data):
            if not isinstance(product_item, dict):
                raise serializers.ValidationError({
                    "products": {str(idx): "Должен быть словарем с полями 'id' и 'quantity'"}
                })
            
            if 'id' not in product_item:
                raise serializers.ValidationError({
                    "products": {str(idx): "Отсутствует обязательное поле 'id'"}
                })
            
            try:
                product = Products.objects.get(pk=product_item['id'])
                validated_products.append({
                    'product': product,
                    'quantity': product_item.get('quantity', 1)
                })
            except Products.DoesNotExist:
                raise serializers.ValidationError({
                    "products": {str(idx): f"Продукт с id {product_item['id']} не найден"}
                })

        data['products'] = validated_products
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data.pop('user', None)
        
        products_data = validated_data.pop('products')
        delivery_address_data = validated_data.pop('delivery_address', None)

        # Создаем адрес доставки
        delivery_address = None
        if delivery_address_data:
            delivery_address_data['user'] = user
            delivery_address = DeliveryAddress.objects.create(**delivery_address_data)

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            status='pending',
            total=0,  # Временное значение
            **validated_data
        )

        # Создаем OrderItems и рассчитываем сумму
        total = 0
        order_items = []
        for product_data in products_data:
            product = product_data['product']
            quantity = product_data['quantity']
            price = product.price * quantity
            total += price
            
            order_items.append(OrderItem(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            ))

        # Массовое создание OrderItems
        OrderItem.objects.bulk_create(order_items)
        
        # Обновляем сумму заказа
        order.total = total
        order.save()

        return order

    def update(self, instance, validated_data):
        # Получаем данные для обновления
        products_data = validated_data.pop('products', None)
        delivery_address_data = validated_data.pop('delivery_address', None)

        # Обновляем основные поля заказа
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Обновляем адрес доставки, если он предоставлен
        if delivery_address_data is not None:
            if instance.delivery_address and delivery_address_data:
                # Обновляем существующий адрес
                delivery_address_serializer = DeliveryAddressSerializer(
                    instance.delivery_address,
                    data=delivery_address_data,
                    partial=True
                )
                delivery_address_serializer.is_valid(raise_exception=True)
                delivery_address_serializer.save()
            elif delivery_address_data:
                # Создаем новый адрес
                user = self.context['request'].user
                delivery_address_data['user'] = user
                instance.delivery_address = DeliveryAddress.objects.create(**delivery_address_data)
            else:
                # Удаляем адрес, если передано null
                instance.delivery_address = None

        # Обновляем товары в заказе, если они предоставлены
        if products_data is not None:
            # Удаляем все существующие OrderItem
            instance.items.all().delete()
            
            # Создаем новые OrderItems и рассчитываем сумму
            total = 0
            order_items = []
            for product_data in products_data:
                product = product_data['product']
                quantity = product_data['quantity']
                price = product.price * quantity
                total += price
                
                order_items.append(OrderItem(
                    order=instance,
                    product=product,
                    quantity=quantity,
                    price=price
                ))

            # Массовое создание OrderItems
            OrderItem.objects.bulk_create(order_items)
            
            # Обновляем сумму заказа
            instance.total = total

        instance.save()
        return instance