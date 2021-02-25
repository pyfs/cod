from datetime import timedelta

from dateutil.utils import today
from django.db.models import Count, Value, CharField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from event.constants import STATUS_REVOKED
from event.serializers import Event, EventListSerializer, EventRetrieveSerializer
from message.serializers import RestAPIMessageListSerializer
from utils.drf.filters import ProjectFilterBackend
from utils.drf.mixins import MultiSerializersMixin


class EventViewSets(MultiSerializersMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin,
                    GenericViewSet):
    queryset = Event.objects.filter(is_removed=False)
    filter_backends = [DjangoFilterBackend, ProjectFilterBackend, SearchFilter]
    serializer_classes = [EventListSerializer, EventRetrieveSerializer]
    search_fields = ['name', 'project__name', 'host']
    filterset_fields = ['project']

    @action(methods=['GET'], detail=True)
    def get_messages(self, request, **kwargs):
        instance = self.get_object()
        serializer = RestAPIMessageListSerializer(instance.messages, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def respond(self, request, **kwargs):
        """认领告警事件"""
        instance = self.get_object()
        instance.responder = request.user
        instance.save()
        serializer = EventRetrieveSerializer(instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def assign(self, request, **kwargs):
        """指派操作人员"""
        instance = self.get_object()
        operators = request.data.get('operators')
        instance.operators.set(operators)
        instance.save()
        serializer = EventRetrieveSerializer(instance)
        return Response(serializer.data)

    @staticmethod
    def get_date_range(request):
        date_start = request.GET.get('date_start', (today() - timedelta(days=15)).strftime('%Y-%m-%d'))
        date_end = request.GET.get('date_end', (today() + timedelta(days=1)).strftime('%Y-%m-%d'))
        return date_start, date_end

    @action(methods=['GET'], detail=False, url_path='event_count_per_day', permission_classes=[])
    def get_event_count_per_day(self, request, *args, **kwargs):
        """按天获取事件数量"""
        date_start, date_end = self.get_date_range(request)
        data = self.queryset.filter(created__gte=date_start, created__lte=date_end).extra(
            select={"date": "to_char(created, 'YYYY-MM-DD')"}).annotate(
            series=Value('event', output_field=CharField())).values('date', 'series').annotate(
            count=Count('created')).order_by('date')
        return Response({'data': data, 'date_range': {'date_start': date_start, 'date_end': date_end}})

    @action(methods=['GET'], detail=False, url_path='top_projects', permission_classes=[])
    def get_top_projects_by_event_count(self, request, *args, **kwargs):
        """根据事件数量聚合计算项目排行榜"""
        date_start, date_end = self.get_date_range(request)
        top = request.GET.get('top', 10)
        data = self.queryset.filter(created__gte=date_start, created__lte=date_end).values('project__name',
                                                                                           'project',
                                                                                           'project__pic__cn_name').annotate(
            count=Count('created')).order_by('-count')[0:int(top)]
        return Response({'data': data, 'date_range': {'date_start': date_start, 'date_end': date_end}})


class EventReceiverFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(receivers__in=[request.user])


class MyEventViewSets(EventViewSets):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['status', 'responder', 'level']

    @action(methods=['POST'], detail=False, url_path='claim')
    def alert_claim(self, request, **kwargs):
        alerts = request.data['alerts']
        count = self.queryset.filter(pk__in=alerts).update(responder=request.user)
        return Response({'message': 'ok', 'count': count})

    @action(methods=['POST'], detail=False, url_path='close')
    def alert_close_manual(self, request, **kwargs):
        alerts = request.data['alerts']
        count = self.queryset.filter(pk__in=alerts).update(status=STATUS_REVOKED)
        return Response({'message': 'ok', 'count': count})
