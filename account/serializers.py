from django.contrib.auth.models import Group
from rest_framework import serializers
from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer

from account.models import User


class GroupSerializer(serializers.ModelSerializer):
    """用户组序列化器"""

    class Meta:
        model = Group
        fields = "__all__"


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器"""
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'cn_name', 'name', 'avatar', 'wx', 'mobile']

    @staticmethod
    def get_name(obj):
        # 为适配 ant design pro CurrentUser
        # 也可以修改 cn_name 为 name 来实现，后续 cc_django 版本更新
        return obj.cn_name or str(obj)


class UserRetrieveSerializer(TaggitSerializer, UserListSerializer):
    groups = GroupSerializer(many=True, read_only=True)
    access = serializers.SerializerMethodField()
    tags = TagListSerializerField()

    class Meta:
        model = User
        fields = ['id', 'name', 'avatar', 'email', 'wx', 'qq', 'mobile', 'signature', 'tags', 'access', 'groups']

    @staticmethod
    def get_access(obj):
        """获取用户权限，ant design pro 直接使用使用 access 单数，此处不再修改"""
        return obj.get_all_permissions()
