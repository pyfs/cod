from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_recursive.fields import RecursiveField
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer

from project.models import Project


class ProjectSerializer(TaggitSerializer, serializers.ModelSerializer):
    children = serializers.ListField(read_only=True, source='get_children', child=RecursiveField())
    tags = TagListSerializerField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'label', 'pic', 'tags', 'children']


class ProjectSimpleSerializer(serializers.ModelSerializer):
    """项目简单字段序列化器"""

    class Meta:
        model = Project
        fields = ['id', 'name', 'label', 'created', 'modified']


class ProjectTreeSerializer(serializers.ModelSerializer):
    """项目简单字段序列化器"""
    key = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    selectable = serializers.SerializerMethodField()
    children = serializers.ListField(read_only=True, source='get_children', child=RecursiveField())

    class Meta:
        model = Project
        fields = ['key', 'title', 'children', 'selectable']

    @staticmethod
    def get_key(obj):
        return obj.id

    @staticmethod
    def get_title(obj):
        return obj.name

    @staticmethod
    def get_selectable(obj):
        if obj.children.count():
            return False
        return True


class ProjectSyncSerializer(serializers.ModelSerializer):
    """项目简单字段序列化器"""
    pic = serializers.CharField(max_length=50, required=True)

    class Meta:
        model = Project
        fields = ['name', 'pic', 'label']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return Project.objects.update_or_create(**validated_data)

    def validate_pic(self, value):
        """
        检验项目负责人的字段是否有效，需要把接口传送过来的域账号转换为用户对象
        """
        # 获取用户对象
        user_model = get_user_model()
        # 查询负责人字段关联的用户
        users = user_model.objects.filter(username=value)
        if not users:
            raise serializers.ValidationError("username not found, check username in COD.")
        return users.last()


class ProjectLeafSerializer(TaggitSerializer, serializers.ModelSerializer):
    """序列化叶子节点"""
    tags = TagListSerializerField()
    parent = RecursiveField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'parent', 'label', 'tags', 'created', 'modified']
        depth = 3
