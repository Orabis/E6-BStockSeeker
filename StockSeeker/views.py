from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


class UserCreate(generics.CreateAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request):
        if request.user.is_authenticated:
            return Response({"detail:" "Deconnecte toi ??"}, status=status.HTTP_403_FORBIDDEN)
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        user = serializers.save()

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "user": serializers.data,
            "refresh": str(refresh),
            "access": str(access_token)
        }, status=status.HTTP_201_CREATED)
