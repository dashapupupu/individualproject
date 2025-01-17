from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'phone_number', 'address', 'email', 'city', 'birth_date', 'avatar')

        def create(self, validated_data):
            return UserProfile.objects.create(**validated_data)
        
        def update(self, instance, validated_data):
            instance.id = validated_data.get('id', instance.id)
            instance.phone_number = validated_data.get('phone_number', instance.phone_number)
            instance.address = validated_data.get('address', instance.address)
            instance.email = validated_data.get('email', instance.email)
            instance.city = validated_data.get('city', instance.city)
            instance.birth_date = validated_data.get('birth_date', instance.birth_date)
            instance.avatar = validated_data.get('avatar', instance.avatar)
            instance.save()
            return instance