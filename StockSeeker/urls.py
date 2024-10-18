from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from .views import *
from . import views
from rest_framework_simplejwt.views import *

##juge pas les noms d'acces OK ?##

router = routers.DefaultRouter()
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/user/create/', CreateUser.as_view(), name="create-user"),
    path('api/user/info', UserInfo.as_view(), name="user-info"),
    path('api/product/create/', CreateProduct.as_view(), name="create-product"),
    path('api/product/list/', ListProduct.as_view(), name="list-product"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name="token_refresh")
]
