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
            return Response({"detail": ["Toujours connecté"]}, status=status.HTTP_403_FORBIDDEN)
        if not request.data.get("email"):
            return Response({"email": ["Saisissez une adresse e-mail valide."]}, status=status.HTTP_400_BAD_REQUEST)
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


class UserInfo(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProductView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def perform_create(self, request):
        if 'quantity' not in request.data or request.data.get('quantity') is None:
            return Response({"quantity": ["give a quantity"]}, status=status.HTTP_400_BAD_REQUEST)
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        serializers.save(user=self.request.user)
        return Response(serializers.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Product.objects.filter(user_id=self.request.user)

