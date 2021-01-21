from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from account.auth import LoginCvte
from account.views import CurrentViewSet, logout, AccountViewSet

router = DefaultRouter()
router.register(r'current', CurrentViewSet)
router.register(r'accounts', AccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/account/', obtain_jwt_token),
    path('login/cvte/', LoginCvte.as_view()),
    path('logout/', logout),
    path('refresh/', refresh_jwt_token),
]
