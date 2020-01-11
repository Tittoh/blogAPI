from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RateAPIView, ArticleAPIView

app_name = "articles"

router = DefaultRouter()
router.register('articles', ArticleAPIView)

urlpatterns = [
    path('', include(router.urls)),
    path('articles/<slug>/rate/', RateAPIView.as_view(), name="rate"),
]
