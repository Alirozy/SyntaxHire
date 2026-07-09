from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer handling secure user registration with email and password only."""
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        validators=[validate_password],
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'user_type', 'created_at']
        read_only_fields = ['id', 'user_type', 'created_at']

    def create(self, validated_data):
        # Uses the CustomUserManager we built earlier to hash password via Argon2
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer to display core user details."""
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']