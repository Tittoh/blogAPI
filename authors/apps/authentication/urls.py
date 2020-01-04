from django.conf.urls import url

from .views import (
    LoginAPIView, RegistrationAPIView, UserRetrieveUpdateAPIView
)

app_name = "authentication"

urlpatterns = [
    url(r'^user/?$', UserRetrieveUpdateAPIView.as_view(), name="user"),
    url(r'^users/?$', RegistrationAPIView.as_view(), name="registration"),
    url(r'^users/login/?$', LoginAPIView.as_view(), name="login"),
]
