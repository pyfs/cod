from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.cache.mixins import ListCacheResponseMixin

from event.serializers import Event, EventListSerializer, EventRetrieveSerializer
from message.serializers import RestAPIMessageListSerializer
from utils.drf.filters import ProjectFilterBackend
from utils.drf.mixins import MultiSerializersMixin
from event.constants import STATUS_REVOKED


class EventViewSets(ListCacheResponseMixin, MultiSerializersMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin,
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
