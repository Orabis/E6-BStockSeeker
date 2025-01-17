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

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            instance.set_password(validated_data.pop('password'))
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    is_stock_low = serializers.SerializerMethodField()

    def validate(self, data):
        if data.get('alert_enabled') and data.get('stock_limit') is None:
            raise serializers.ValidationError({
                'product_stock_limit': "Ce champ est obligatoire si une alerte est activée."
            })
        return data
    
    class Meta:
        model = Product
        fields = ["id", "name", "description", "quantity", "creation_date", "modification_date", "user","stock_limit","alert_enabled","is_stock_low"]

    def get_is_stock_low(self, obj):
        if not isinstance(obj, Product):
            return None
        return obj.is_stock_low