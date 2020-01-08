from django.conf.urls import url

from .views import ProfileRetrieveAPIView

app_name = 'profiles'

urlpatterns = [
    url(r'^(?P<username>\w+)/?$',
        ProfileRetrieveAPIView.as_view(), name="view_profile"),

]
