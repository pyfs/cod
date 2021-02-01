import json

from rest_framework.serializers import ModelSerializer

from message.models import Message
from utils.drf.decorators import validate_field_value
from utils.drf.serializers import RobustSerializer


class RestAPIMessageListSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'project', 'type', 'extra', 'host', 'title', 'level', 'status', 'data_source', 'created',
                  'modified']


class RestAPICreateMessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'


class PrometheusMessageSerializer(RobustSerializer):
    class Meta:
        model = Message
        fields = '__all__'

    @staticmethod
    @validate_field_value
    def get_project(field, data):
        """获取项目名称"""
        try:
            return '%s_%s' % (data['labels'].get("productline"), data['labels'].get("product"))
        except KeyError:
            return 'Prometheus'

    @staticmethod
    @validate_field_value
    def get_type(field, data):
        """获取告警标识"""
        return data['labels'].get("alertname", "")

    @staticmethod
    @validate_field_value
    def get_host(field, data):
        """获取告警主机"""
        return data['labels'].get("ipaddress", "")

    @staticmethod
    @validate_field_value
    def get_title(field, data):
        """获取告警标题"""
        return data['annotations'].get("summary", "")

    @staticmethod
    @validate_field_value
    def get_level(field, data):
        """获取告警等级"""
        level = data['labels'].get('severity', "")
        mapping = {"warning": 0, "critical": 1, "disaster": 2}
        return mapping[level]

    @staticmethod
    @validate_field_value
    def get_status(field, data):
        """获取告警状态"""
        status = data['status']
        mapping = {"firing": 'alert', "resolved": 'recover'}
        return mapping[status]

    @staticmethod
    @validate_field_value
    def get_extra(field, data):
        """获取告警原始数据"""
        extra_data = data['labels']
        extra_data['desc'] = data['annotations'].get("description", "")
        extra_data["summary"] = data['annotations'].get("summary", "")
        return json.dumps(extra_data)

    @staticmethod
    @validate_field_value
    def get_tags(field, data):
        """获取告警标签"""
        return ""

    @staticmethod
    @validate_field_value
    def get_data_source(field, data):
        """获取告警数据源"""
        return data['data_source']
