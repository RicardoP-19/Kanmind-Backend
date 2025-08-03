from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializer import RegistrationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from .serializer import RegistrationSerializer, LoginSerializer


"""
API endpoint for user registration.
Allows any user (AllowAny) to register by providing email, password and full name.
Upon successful registration, an authentication token is generated and returned
along with the user's data.
"""
class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            saved_account = serializer.save()
            token, created = Token.objects.get_or_create(user=saved_account)
            data = {
                'token': token.key,
                'fullname': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id
            }
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

"""
API endpoint for user login via email and password.
Accepts user credentials and returns a valid token and user data upon successful authentication.
"""
class LoginView(ObtainAuthToken):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email,
                'user_id': user.id
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)