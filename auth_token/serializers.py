from rest_framework import serializers
from django.contrib.auth import authenticate


class AuthTokenSerializer(serializers.Serializer):
    """ todo update 和 create 不需要，可删除 for sh (不确定该功能，暂存)"""

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    username = serializers.CharField(label="用户名")
    password = serializers.CharField(
        label="密码",
        style={'input_type': 'password'},
        trim_whitespace=True
    )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
