import logging
from datetime import timedelta

from dateutil.utils import today
from django.db.models import Count, Value, CharField
from django_filters.rest_framework import DjangoFilterBackend
from jsonpath_rw import parse
from rest_framework import status
from rest_framework.authentication import get_authorization_header
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.mixins import CacheResponseMixin

from auth_token.models import AuthToken
from data_source.authentications import TokenAuthentication
from message.models import Message
from message.serializers import RestAPICreateMessageSerializer, PrometheusMessageSerializer
from utils.drf.mixins import MultiSerializersMixin

logger = logging.getLogger('django')


class RestAPIMessageViewSets(CacheResponseMixin, MultiSerializersMixin, CreateModelMixin, GenericViewSet):
    queryset = Message.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    serializer_classes = [RestAPICreateMessageSerializer]
    search_fields = ['project', 'type', 'host', 'title', 'desc']
    authentication_classes = [TokenAuthentication]

    def create(self, request, *args, **kwargs):
        """
        todo 待做异常处理 for sh
        1. data_source 可能为空
        todo 校验 extra 数据是否可被 JSON 化 for sh
        """
        data_source = self.get_data_source(request, *args, **kwargs)
        try:
            # 接口提交数据是通过form格式则需要单独开启编辑功能，JSON类型则不需要
            # 开启修改QueryDictionary
            request.data._mutable = True
        except AttributeError:
            logger.debug("request.data._mutable is no attribute")
        # 增加数据源标识
        request.data['data_source'] = data_source
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @staticmethod
    def get_data_source(request, *args, **kwargs):
        # 获取数据源, str: data source name
        token = request.query_params.get('token') or get_authorization_header(request).split()[1]
        return AuthToken.objects.get(token=token).data_source.name


class PrometheusMessageViewSets(CreateModelMixin, GenericViewSet):
    """ Prometheus 专用接口"""
    queryset = Message.objects.filter()
    serializer_class = PrometheusMessageSerializer
    authentication_classes = [TokenAuthentication]

    @staticmethod
    def get_loop_data(data):
        """根据 Meta loop 字段获取循环数据"""
        loop = 'alerts'  # 根据该字段循环
        data_list = list()

        if loop:
            jsonpath_expr = parse(loop)
            loop_data_list = [match.value for match in jsonpath_expr.find(data)]
            for loop_data in loop_data_list:
                if isinstance(loop_data, list):
                    data_list += loop_data
                elif isinstance(loop_data, dict):
                    data_list.append(loop_data)
                else:
                    pass
        else:
            data_list.append(data)

        return data_list

    def create(self, request, *args, **kwargs):
        response_data = list()
        token = request.query_params.get('token') or get_authorization_header(request).split()[1]
        data_source = AuthToken.objects.get(token=token).data_source.name
        for data in self.get_loop_data(request.data):
            data['data_source'] = data_source
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response_data.append(serializer.data)
        return Response({"data": response_data}, status=status.HTTP_201_CREATED)


class MessageViewSets(MultiSerializersMixin, GenericViewSet):
    queryset = Message.objects.filter()

    @staticmethod
    def get_date_range(request):
        date_start = request.GET.get('date_start', (today() - timedelta(days=15)).strftime('%Y-%m-%d'))
        date_end = request.GET.get('date_end', (today() + timedelta(days=1)).strftime('%Y-%m-%d'))
        return date_start, date_end

    @action(methods=['GET'], detail=False, url_path='message_count_per_day', permission_classes=[])
    def get_message_count_per_day(self, request, *args, **kwargs):
        """按天获取消息数量"""
        date_start, date_end = self.get_date_range(request)
        message_count_per_day = self.queryset.filter(created__gte=date_start, created__lte=date_end).extra(
            select={"date": "to_char(created, 'YYYY-MM-DD')"}).annotate(
            series=Value('message', output_field=CharField())).values('date', 'series').annotate(
            count=Count('created')).order_by('date')
        return Response({'data': message_count_per_day, 'date_range': {'date_start': date_start, 'date_end': date_end}})

