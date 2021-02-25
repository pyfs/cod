from django.urls import path, include
from rest_framework.routers import DefaultRouter

from message.views import RestAPIMessageViewSets, PrometheusMessageViewSets, MessageViewSets

router = DefaultRouter()
router.register(r'restapi', RestAPIMessageViewSets)
router.register(r'prometheus', PrometheusMessageViewSets)
router.register(r'messages', MessageViewSets)

urlpatterns = [
    path('', include(router.urls)),
]
