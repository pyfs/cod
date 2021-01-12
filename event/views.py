from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from event.serializers import Event, EventListSerializer, EventRetrieveSerializer
from message.serializers import RestAPIMessageListSerializer
from utils.drf.filters import ProjectFilterBackend
from utils.drf.mixins import MultiSerializersMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework_extensions.mixins import CacheResponseMixin
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response


class EventViewSets(CacheResponseMixin, MultiSerializersMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin,
                    GenericViewSet):
    queryset = Event.objects.filter(is_removed=False)
    filter_backends = [DjangoFilterBackend, ProjectFilterBackend, SearchFilter]
    serializer_classes = [EventListSerializer, EventRetrieveSerializer]
    search_fields = ['name', 'project__name', 'host']
    filter_fields = ['project']

    @action(methods=['GET'], detail=True)
    def get_messages(self, request, **kwargs):
        event = Event.objects.get(pk=kwargs['pk'])
        serializer = RestAPIMessageListSerializer(event.messages, many=True)
        return Response(serializer.data)
