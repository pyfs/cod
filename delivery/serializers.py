from rest_framework import serializers
from delivery.models import Delivery
from rest_framework_recursive.fields import RecursiveField
from account.serializers import UserListSerializer


class DeliveryListSerializer(serializers.ModelSerializer):
    receivers = UserListSerializer(read_only=True, many=True)
    children = serializers.ListField(read_only=True, source='get_children', child=RecursiveField())

    class Meta:
        model = Delivery
        fields = ['id', 'name', 'receivers', 'created', 'modified', 'children']
        depth = 1
