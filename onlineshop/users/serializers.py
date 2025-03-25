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
        fields = ['id', 'name']  # Отобразите необходимые поля

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Products.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
    
    def validate(self, attrs):
        # Убедитесь, что есть хотя бы одно поле продукта
        if attrs['quantity'] <= 0:
            raise serializers.ValidationError({"quantity": "Количество должно быть положительным."})
        return attrs

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'delivery_address', 'delivery_type', 'total', 'status', 'ready_at', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        total = 0
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            total += item_data['quantity'] * item_data['price']  # Считаем общую стоимость
        
        order.total = total  # Устанавливаем общую стоимость заказа
        order.save()
        
        return order