from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.models import User


"""
Serializes and validates user registration data.
Ensures password confirmation matches and email is unique.
"""
class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True)
    fullname = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self):
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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value
    

"""
Validates login credentials and authenticates the user by email and password.
"""
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
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