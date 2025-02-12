from rest_framework import serializers
from .models import CustomUser, Profile
from django.contrib.auth.password_validation import validate_password

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user details"""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'unique_id']


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2', 'unique_id')

    def validate_email(self, value):
        """
        Ensure the email is unique.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate(self, data):
        """
        Ensure that passwords match.
        """
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password1')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user profile"""
    user = CustomUserSerializer(read_only=True)  # Embed user details
    unique_id = serializers.CharField(source='user.unique_id', read_only=True)  # Include unique_id from CustomUser

    class Meta:
        model = Profile
        fields = ['user', 'image', 'phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country', 'old_cart', 'unique_id']
