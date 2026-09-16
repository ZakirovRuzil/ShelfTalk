from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import LoginSerializer
from .views import CurrentUserView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", TokenObtainPairView.as_view(serializer_class=LoginSerializer)),
    path("refresh/", TokenRefreshView.as_view()),
    path("me/", CurrentUserView.as_view()),
]
