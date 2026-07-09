from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    Endpoint for frictionless user onboarding.
    POST /api/accounts/register/
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny] # Public access
    serializer_class = RegisterSerializer


class MeView(APIView):
    """
    Retrieve authenticated user's core profile information.
    GET /api/accounts/me/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)