from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.mixins import CacheResponseMixin

from data_source.authentications import TokenAuthentication
from project.serializers import Project, ProjectTreeSerializer, ProjectSyncSerializer


class ProjectViewSet(CacheResponseMixin, ModelViewSet):
    queryset = Project.objects.filter(parent=None)
    serializer_class = ProjectTreeSerializer

    @cache_response()
    @action(methods=['GET'], detail=False)
    def get_user_projects(self, request, **kwargs):
        projects = Project.objects.filter(
            Q(pic=request.user) | Q(members__in=[request.user]) | Q(subscribers__in=[request.user]))
        plist = [p.get_root() for p in projects]
        serializer = ProjectTreeSerializer(plist, many=True)
        return Response(serializer.data)

    @cache_response()
    @action(methods=['POST'], detail=True)
    def subscribe(self, request, **kwargs):
        current = request.user
        pk = kwargs.get('pk')
        try:
            project = Project.objects.get(pk=pk)
            project.subscribers.add(current)
            return Response({'status': 'ok', 'data': 'subscribed'})
        except Exception as e:
            return Response({'status': 'error', 'data': e})

    @cache_response()
    @action(methods=['POST'], detail=True)
    def unsubscribe(self, request, **kwargs):
        current = request.user
        pk = kwargs.get('pk')
        try:
            project = Project.objects.get(pk=pk)
            project.subscribers.remove(current)
            return Response({'status': 'ok', 'data': 'unsubscribed'})
        except Exception as e:
            return Response({'status': 'error', 'data': e})

    @action(methods=['POST'], detail=False, authentication_classes=[TokenAuthentication],
            serializer_class=ProjectSyncSerializer, permission_classes=[])
    def sync(self, request, *args, **kwargs):
        """
        用于项目同步创建使用，接口地址参考如下
        http://127.0.0.1:8080/v1/project/projects/sync/
        接口核心功能同步项目的所有操作，如果项目不存在的话，直接创建，有的话就更新。
        """
        # 校验数据
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        # todo 反序列表处理serializer.data 数据，暂时返回request.data
        # todo 输出规范的日志
        return Response(request.data, status.HTTP_200_OK)
