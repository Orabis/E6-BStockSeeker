from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from .views import *
from . import views

router = routers.DefaultRouter()
router.register(r'product', views.ProductViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path("create/", UserCreate.as_view(), name="user-create")
]
