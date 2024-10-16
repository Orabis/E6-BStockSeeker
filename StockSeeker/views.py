from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.throttling import UserRateThrottle
from rest_framework.response import Response
from rest_framework import generics, status


class UserCreate(generics.CreateAPIView):
    throttle_classes = [UserRateThrottle]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request):
        serializers = self.get_serializer(data=request.data)
        serializers.is_valid(raise_exception=True)
        user = serializers.save()
        return Response(serializers.data, status=status.HTTP_201_CREATED)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CreateProject(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)
