from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import BaseFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.mixins import CacheResponseMixin

from event.serializers import Event, EventListSerializer, EventRetrieveSerializer
from message.serializers import RestAPIMessageListSerializer
from utils.drf.filters import ProjectFilterBackend
from utils.drf.mixins import MultiSerializersMixin
from event.constants import STATUS_REVOKED


class EventViewSets(CacheResponseMixin, MultiSerializersMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin,
                    GenericViewSet):
    queryset = Event.objects.filter(is_removed=False)
    filter_backends = [DjangoFilterBackend, ProjectFilterBackend, SearchFilter]
    serializer_classes = [EventListSerializer, EventRetrieveSerializer]
    search_fields = ['name', 'project__name', 'host']
    filter_fields = ['project']

    @action(methods=['GET'], detail=True)
    def get_messages(self, request, **kwargs):
        event = self.queryset.get(pk=kwargs['pk'])
        serializer = RestAPIMessageListSerializer(event.messages, many=True)
        return Response(serializer.data)


class EventReceiverFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(receivers__in=[request.user])


class MyEventViewSets(EventViewSets):
    filter_backends = [DjangoFilterBackend, SearchFilter, EventReceiverFilter]
    filterset_fields = ['status', 'responder']

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
