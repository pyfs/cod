from event.models import Event
from rest_framework.serializers import ModelSerializer
from project.serializers import ProjectSimpleSerializer, ProjectSerializer
from data_source.serializers import DataSourceSerializer
from delivery.serializers import DeliveryListSerializer, UserListSerializer
from account.serializers import UserListSerializer


class EventListSerializer(ModelSerializer):
    project = ProjectSimpleSerializer(read_only=True)
    ds = DataSourceSerializer(read_only=True)
    responder = UserListSerializer(read_only=True)

    class Meta:
        model = Event
        exclude = ['is_removed', 'start', 'end', 'status_changed', 'similar', 'receivers', 'operators', 'converge']


class EventRetrieveSerializer(ModelSerializer):
    project = ProjectSerializer(read_only=True)
    ds = DataSourceSerializer(read_only=True)
    current_delivery = DeliveryListSerializer(read_only=True)
    receivers = UserListSerializer(read_only=True, many=True)
    responder = UserListSerializer(read_only=True)

    class Meta:
        model = Event
        exclude = ['is_removed', 'start', 'end', 'similar', 'messages']
