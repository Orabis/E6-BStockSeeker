from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.db.models import F
from django.db import transaction
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
        fields = ["id", "name", "description", "quantity", "creation_date", "modification_date", "user","stock_limit","alert_enabled","is_stock_low","image","warehouses","reference"]

    def create(self, validated_data):
        warehouses = validated_data.pop('warehouses', [])
        
        with transaction.atomic():
            product = Product.objects.create(**validated_data)
            product.warehouses.set(warehouses)
            product.refresh_from_db()
            for warehouse in product.warehouses.all():
                warehouse.refresh_from_db()
                if warehouse.actual_capacity - product.quantity < 0:
                    raise serializers.ValidationError({
                        'quantity': ["L'entrepôt n'a plus assez de place"]
                    })
                warehouse.actual_capacity = F('actual_capacity') - product.quantity
                warehouse.save(update_fields=['actual_capacity'])

        return product
    
    def update(self, instance, validated_data):
        new_quantity = validated_data.get("quantity", instance.quantity)
        new_warehouses = validated_data.pop('warehouses', [])

        old_warehouses = list(instance.warehouses.all())
        old_quantity = instance.quantity 
        
        with transaction.atomic():
            for warehouse in old_warehouses:
                warehouse.refresh_from_db()
                warehouse.actual_capacity = F('actual_capacity') + old_quantity
                warehouse.save(update_fields=['actual_capacity'])

            instance.name = validated_data.get("name", instance.name)
            instance.description = validated_data.get("description", instance.description)
            instance.reference = validated_data.get("reference", instance.reference)
            instance.quantity = new_quantity
            instance.save()

            instance.warehouses.set(new_warehouses)
            instance.refresh_from_db()

            for warehouse in instance.warehouses.all():
                warehouse.refresh_from_db()
                if warehouse.actual_capacity - new_quantity < 0:
                    raise serializers.ValidationError({
                        'quantity': ["L'entrepôt n'a plus assez de place"]
                    })
                warehouse.actual_capacity = F('actual_capacity') - new_quantity
                warehouse.save(update_fields=['actual_capacity'])

            return instance

    
    def destroy(self, instance):
        with transaction.atomic():
            for warehouse in instance.warehouses.all():
                warehouse.refresh_from_db()
                warehouse.actual_capacity = F('actual_capacity') + instance.quantity
                warehouse.save(update_fields=['actual_capacity'])
            instance.delete()
    
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

    def update(self, instance, validated_data):
        old_max_capacity = instance.max_capacity

        with transaction.atomic():
            instance.name = validated_data.get("name", instance.name)
            instance.location = validated_data.get("location", instance.location)
            new_max_capacity = validated_data.get("max_capacity", instance.max_capacity)

            capacity_difference = new_max_capacity - old_max_capacity

            new_actual_capacity = instance.actual_capacity + capacity_difference
            if new_actual_capacity < 0:
                raise serializers.ValidationError({
                    'max_capacity': ["La réduction de la capacité maximale entraînerait une capacité actuelle négative."]
                })

            instance.actual_capacity = F('actual_capacity') + capacity_difference
            instance.max_capacity = new_max_capacity

            instance.save()
            instance.refresh_from_db()

        return instance
    
    class Meta:
        model = Warehouse
        fields = ["id", "name", "location", "max_capacity","user","actual_capacity"]
    
    def create(self, validated_data):
        validated_data["actual_capacity"] = validated_data.get("max_capacity",0)
        return Warehouse.objects.create(**validated_data)
    
    def validate_max_capacity(self, value):
        if value < 0:
            raise serializers.ValidationError("La capacité maximale ne peut pas être négative.")
        return value