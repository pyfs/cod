from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import CacheResponseMixin
from data_source.serializers import DataSource, DataSourceSerializer
from django_filters.rest_framework import DjangoFilterBackend


class DataSourceViewSets(CacheResponseMixin, ModelViewSet):
    queryset = DataSource.objects.all()
    serializer_class = DataSourceSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'label']
