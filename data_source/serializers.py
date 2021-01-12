from rest_framework import serializers
from data_source.models import DataSource
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class DataSourceSerializer(TaggitSerializer, serializers.ModelSerializer):
    # tags = TagListSerializerField()

    class Meta:
        model = DataSource
        fields = ['id', 'name', 'label', 'close_timeout', 'status', 'is_enabled', 'created', 'modified']
