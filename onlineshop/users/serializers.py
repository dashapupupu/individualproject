from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Order, DeliveryAddress, OrderItem


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
    

    
class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    delivery_address = serializers.PrimaryKeyRelatedField(queryset=DeliveryAddress.objects.all(), allow_null=True) 
    order_item = serializers.PrimaryKeyRelatedField(queryset=OrderItem.objects.all(), allow_null=True) 
    class Meta:
        model = Order
        fields = ('id', 'user', 'order_date', 'delivery_address', 'order_item', 'delivery_type', 'total', 'status', 'ready_at')
        read_only_fields = ('id', 'order_date')