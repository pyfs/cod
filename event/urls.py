from rest_framework.routers import DefaultRouter
from django.urls import path, include
from event.views import EventViewSets

router = DefaultRouter()
router.register(r'events', EventViewSets)

urlpatterns = [
    path('', include(router.urls)),
]
