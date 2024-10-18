from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(null=False, max_length=30, blank=False)
    description = models.CharField(default=None, null=True, blank=True, max_length=120)
    quantity = models.IntegerField(null=False, default=0, blank=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.name


class Alerte(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE, related_name="alert")
    stock_limit = models.IntegerField(null=False, blank=False)
    message = models.CharField(max_length=200, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    modification_date = models.DateTimeField(auto_now=True)
