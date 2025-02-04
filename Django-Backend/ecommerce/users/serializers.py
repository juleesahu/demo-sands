from rest_framework import serializers
from .models import CustomUser, Profile
from django.contrib.auth.password_validation import validate_password

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user details"""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'unique_id']

class CustomUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, required=True, min_length=8, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'password', 'confirm_password')

    def validate_email(self, value):
        """Ensure the email is unique"""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        """Check that both passwords match"""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        """Create a new user with an automatically generated unique_id"""
        validated_data.pop('confirm_password')  # Remove confirm_password since it's not in the model
        password = validated_data.pop('password')

        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the user profile"""
    user = CustomUserSerializer(read_only=True)  # Embed user details

    class Meta:
        model = Profile
        fields = ['user', 'image', 'phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country', 'old_cart']
