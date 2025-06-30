from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegisterView(APIView):
    def post(self, request):
        return Response({"message": "Registrierung erfolgreich (Demo)."}, status=status.HTTP_201_CREATED)