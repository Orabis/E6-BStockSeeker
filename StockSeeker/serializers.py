from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse e-mail est déjà utilisée.")
        return value


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "quantity", "creation_date", "modification_date"]


class AlerteSerializer(serializers.ModelSerializer):
    product = ProductSerializer

    class Meta:
        model = Alerte
        fields = ["id", "product", "stock_limit", "message", "creation_date", "modification_date"]
