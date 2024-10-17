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
    path('create/', UserCreate.as_view(), name="user-create"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name="token_refresh")
]
