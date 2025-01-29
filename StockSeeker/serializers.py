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
    warehouses = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        many=True
    )

    def validate(self, data):
        if data.get('alert_enabled') and data.get('stock_limit') is None:
            raise serializers.ValidationError({
                'product_stock_limit': "Ce champ est obligatoire si une alerte est activée."
            })
        return data
    
    class Meta:
        model = Product
        fields = ["id", "name", "description", "quantity", "creation_date", "modification_date", "user","stock_limit","alert_enabled","is_stock_low","image","warehouses",]

    def create(self, validated_data):
        warehouses = validated_data.pop('warehouses', [])
        product = Product.objects.create(**validated_data)
        product.warehouses.set(warehouses)

        for warehouse in product.warehouses.all():
            print(f'capacité actuelle {warehouse.actual_capacity}, - {product.quantity}')
            warehouse.actual_capacity -= product.quantity
            warehouse.save()
        return product
    
    def update(self,instance, validated_data):
        product = Product.objects.get(id=instance.id)
        instance.name = validated_data.get("name", instance.name)
        instance.description = validated_data.get("description", instance.description)
        instance.quantity = validated_data.get("quantity", instance.quantity)
        instance.save()

        for warehouse in product.warehouses.all():
            warehouse.actual_capacity = warehouse.max_capacity
            warehouse.actual_capacity -= instance.quantity
            warehouse.save()
        return instance
    
    def destroy(self, instance):
        product = Product.objects.get(id=instance.id)
        
        for warehouse in product.warehouses.all():
            warehouse.actual_capacity += instance.quantity
            warehouse.save()
        instance.delete()
        return instance
    
    def validate_warehouses(self, value):
        if not value:
            raise serializers.ValidationError("Un produit doit être associé à au moins un entrepôt.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("La quantité ne peut pas être négative.")
        return value
    
    def get_is_stock_low(self, obj):
        return obj.alert_enabled and obj.stock_limit is not None and obj.quantity < obj.stock_limit
    
class WarehouseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Warehouse
        fields = ["id", "name", "location", "max_capacity","user","actual_capacity"]
    
    def validate_max_capacity(self, value):
        if value < 0:
            raise serializers.ValidationError("La capacité maximale ne peut pas être négative.")
        return value