from django.conf.urls import url
from django.urls import path

from .views import (ProfileRetrieveAPIView,
                    ProfileFollowAPIView, FollowersAPIView, FollowingAPIView)

app_name = 'profiles'

urlpatterns = [
    path('<username>/', ProfileRetrieveAPIView.as_view(), name="view_profile"),
    path('<username>/follow/',
         ProfileFollowAPIView.as_view(), name="follow_profile"),
    path('<username>/followers/',
         FollowersAPIView.as_view(), name="followers"),
    path('<username>/following/',
         FollowingAPIView.as_view(), name="following"),
]
