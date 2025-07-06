from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User
class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializes and validates user registration data.
    Ensures password confirmation matches and email is unique.
    """
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
        """
        Creates a new user with a hashed password.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        username = self.validated_data['fullname']

        if pw != repeated_pw:
            raise serializers.ValidationError({'error':'password dont match'})      
          
        account = User(email=self.validated_data['email'], username=self.validated_data['fullname'])
        account.set_password(pw)
        account.save()
        return account
        
    def validate_email(self, value):
        """
        Validates that the email address is not already taken.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value
class LoginSerializer(serializers.Serializer):
    """
    Validates login credentials and authenticates the user by email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Checks if a user with the provided email exists and the password is correct.
        Adds the authenticated user to the validated data.
        """
        email = data.get('email')
        password = data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': 'Invalid credentials.'})

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError({'error': 'Invalid credentials.'})
        data['user'] = user
        return data