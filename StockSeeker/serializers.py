from rest_framework import serializers

from .models import *


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "quantity", "creation_date", "modification_date"]


class AlerteSerializer(serializers.ModelSerializer):
    product = ProductSerializer

    class Meta:
        model = Alerte
        fields = ["id", "product", "stock_limit", "message", "creation_date", "modification_date"]
