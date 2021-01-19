from rest_framework.routers import DefaultRouter
from django.urls import path, include
from event.views import EventViewSets, MyEventViewSets

router = DefaultRouter()
router.register(r'events', EventViewSets)
router.register(r'my-alerts', MyEventViewSets)

urlpatterns = [
    path('', include(router.urls)),
]
