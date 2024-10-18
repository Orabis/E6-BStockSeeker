from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


class CreateUser(generics.CreateAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request):
        if request.user.is_authenticated:
            return Response({"detail:" "Deconnecte toi ??"}, status=status.HTTP_403_FORBIDDEN)
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save()

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            "user": serializers.data,
            "refresh": str(refresh),
            "access": str(access_token)
        }, status=status.HTTP_201_CREATED)


class UserInfo(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(username=self.request.user)


class CreateProduct(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def create(self, request):
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(user=request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class ListProduct(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user_id=self.request.user)
