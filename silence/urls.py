from django.urls import path, include
from rest_framework.routers import DefaultRouter
from silence.views import SilenceViewSet


router = DefaultRouter()
router.register(r'silences', SilenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
