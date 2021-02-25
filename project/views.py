from datetime import timedelta

from dateutil.utils import today
from django.db.models import Count, Value, CharField, Q
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework_extensions.cache.decorators import cache_response
from rest_framework_extensions.mixins import CacheResponseMixin

from data_source.authentications import TokenAuthentication
from message.models import Message
from project.serializers import Project, ProjectTreeSerializer, ProjectSyncSerializer, ProjectLeafSerializer


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


class ProjectReportViewSet(CacheResponseMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectLeafSerializer

    @staticmethod
    def get_date_range(request):
        date_start = request.GET.get('date_start', (today() - timedelta(days=15)).strftime('%Y-%m-%d'))
        date_end = request.GET.get('date_end', (today() + timedelta(days=1)).strftime('%Y-%m-%d'))
        return date_start, date_end

    @action(methods=['GET'], detail=True)
    def event(self, request, *args, **kwargs):
        """
        permission_classes=[]
        任何人都有权限查看项目报表，如果需要控制权限，请自行添加权限认证
        """
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        events = instance.event_set.filter(created__gte=date_start, created__lte=date_end).extra(
            select={"date": "to_char(created, 'YYYY-MM-DD')"}).annotate(
            series=Value('event', output_field=CharField())).values('date', 'series').annotate(
            count=Count('created')).order_by('date')
        return Response({'data': events, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=True)
    def message(self, request, *args, **kwargs):
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        messages = Message.objects.filter(created__gte=date_start, created__lte=date_end,
                                          project=instance.label).extra(
            select={"date": "to_char(created, 'YYYY-MM-DD')"}).annotate(
            series=Value('message', output_field=CharField())).values('date', 'series').annotate(
            count=Count('created')).order_by('date')
        return Response({'data': messages, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=True)
    def top_types(self, request, *args, **kwargs):
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        top = request.GET.get('top', 20)
        types = instance.event_set.filter(created__gte=date_start, created__lte=date_end).values('type',
                                                                                                 'current_delivery__name').annotate(
            count=Count('type')).order_by('count')[0: int(top)]
        return Response({'data': types, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=True)
    def level_percent(self, request, *args, **kwargs):
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        levels = instance.event_set.filter(created__gte=date_start, created__lte=date_end).values('level').annotate(
            count=Count('level'))
        return Response({'data': levels, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=True)
    def host_percent(self, request, *args, **kwargs):
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        hosts = instance.event_set.filter(created__gte=date_start, created__lte=date_end).values('host').annotate(
            count=Count('host'))
        return Response({'data': hosts, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=True)
    def status_percent(self, request, *args, **kwargs):
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        states = instance.event_set.filter(created__gte=date_start, created__lte=date_end).values('status').annotate(
            count=Count('status'))
        return Response({'data': states, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=True)
    def receivers_percent(self, request, *args, **kwargs):
        instance = self.get_object()
        date_start, date_end = self.get_date_range(request)
        receivers = instance.event_set.filter(created__gte=date_start, created__lte=date_end).values(
            'receivers__cn_name').annotate(count=Count('receivers'))
        return Response({'data': receivers, 'date_range': {'date_start': date_start, 'date_end': date_end}})