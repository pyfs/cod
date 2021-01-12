from rest_framework.decorators import action
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from account.serializers import User, UserRetrieveSerializer
from project.serializers import ProjectSimpleSerializer
from django.http.response import HttpResponseRedirect


class CurrentViewSet(GenericViewSet):
    """获取当前登录用户信息"""
    queryset = User.objects.filter(is_active=True, is_removed=False)
    authentication_classes = [JSONWebTokenAuthentication]

    @cache_response()
    @action(methods=['GET'], detail=False, url_path='user')
    def get_current_user(self, request, **kwargs):
        serializer = UserRetrieveSerializer(request.user)
        return Response(serializer.data)

    @cache_response()
    @action(methods=['GET'], detail=False)
    def get_projects_subscribed(self, request, **kwargs):
        projects_subscribed = request.user.subscribe_project.all()
        data_subscribed = ProjectSimpleSerializer(projects_subscribed, many=True).data
        return Response(data_subscribed)

    @cache_response()
    @action(methods=['GET'], detail=False)
    def get_projects_charged(self, request, **kwargs):
        projects_charged = request.user.charged_project.all()
        serializer = ProjectSimpleSerializer(projects_charged, many=True)
        return Response(serializer.data)

    @cache_response()
    @action(methods=['GET'], detail=False)
    def get_projects_belong_to(self, request, **kwargs):
        projects_belong_to = request.user.belong_to_project.all()
        serializer = ProjectSimpleSerializer(projects_belong_to, many=True)
        return Response(serializer.data)


def logout(request, **kwargs):
    """logout"""
    response = HttpResponseRedirect('/')
    response.delete_cookie(key='JWT')
    return response