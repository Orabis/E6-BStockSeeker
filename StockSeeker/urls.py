from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from .views import *
from . import views
from rest_framework_simplejwt.views import *
from drf_spectacular.views import SpectacularAPIView


router = routers.DefaultRouter()
router.register(r'products', ProductView, basename='product')
router.register(r'warehouses', WarehouseView, basename='warehouse')

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/users', CreateUser.as_view(), name="create-user"),
    path('api/users/me/', UserInfo.as_view(), name="user-info"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema')]
