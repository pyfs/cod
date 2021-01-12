from rest_framework.routers import DefaultRouter
from django.urls import path, include
from data_source.views import DataSourceViewSets

router = DefaultRouter()
router.register(r'data_sources', DataSourceViewSets)


urlpatterns = [
    path('', include(router.urls)),
]
