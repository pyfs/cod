from django.urls import path, include
from rest_framework.routers import DefaultRouter

from project.views import ProjectViewSet, ProjectReportViewSet

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'reports', ProjectReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
