from rest_framework.routers import DefaultRouter
from django.urls import path, include
from message.views import RestAPIMessageViewSets, PrometheusMessageViewSets

router = DefaultRouter()
router.register(r'restapi', RestAPIMessageViewSets)
router.register(r'prometheus', PrometheusMessageViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
