from django.conf.urls import url
from django.urls import path

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView, VerifyAccount, SocialAuthView
)

app_name = "authentication"

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user"),
    path('users/', RegistrationAPIView.as_view(), name="registration"),
    path('users/login/', LoginAPIView.as_view(), name="login"),
    path('users/verify/<uidb64>/<token>/',
         VerifyAccount.as_view(), name="verify"),
    path("oauth/", SocialAuthView.as_view(), name="oauth"),
]
