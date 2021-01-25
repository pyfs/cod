import logging

from django.conf import settings
from django.db import models
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel, StatusModel, SoftDeletableModel, UUIDModel
from taggit.managers import TaggableManager
from datetime import timedelta
from pytz import timezone

from converge.models import BurrConverge
from data_source.models import DataSource
from delivery.models import Delivery
from event.constants import STATUS_NO_RESPONSE, STATUS_PROCESSING, STATUS_RESOLVED, STATUS_REVOKED, STATUS_TIMEOUT, \
    STATUS_NOT_CLOSED
from message.constants import LEVEL_CHOICES, LEVEL_WARNING
from message.models import Message
from project.models import Project
from utils.common.models import OwnerModel, DateTimeFramedModel, ExtraModel
from utils.taggit.models import TaggedUUIDItem


logger = logging.getLogger('django')


class Event(UUIDModel, DateTimeFramedModel, TimeStampedModel, StatusModel, SoftDeletableModel, ExtraModel):
    """告警事件"""
    STATUS = Choices(STATUS_NO_RESPONSE, STATUS_PROCESSING, STATUS_RESOLVED, STATUS_REVOKED, STATUS_TIMEOUT)
    name = models.CharField(verbose_name='事件名称', max_length=120)
    project = models.ForeignKey(Project, verbose_name='所属项目', on_delete=models.CASCADE)
    host = models.CharField(verbose_name='主机标识', max_length=128)
    level = models.PositiveSmallIntegerField(verbose_name='事件级别', choices=LEVEL_CHOICES, default=LEVEL_WARNING)
    type = models.CharField(verbose_name='事件类型', max_length=50)
    ds = models.ForeignKey(DataSource, verbose_name='数据源', on_delete=models.CASCADE)
    current_delivery = models.ForeignKey(Delivery, verbose_name='分派策略',
                                         on_delete=models.SET_NULL,
                                         null=True,
                                         blank=True)
    messages = models.ManyToManyField(Message, verbose_name='关联消息')
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       verbose_name='消息接收人',
                                       related_name='receive_events',
                                       blank=True)
    responder = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='响应人员', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='respond_event')
    operators = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='处理人员', related_name='operate_events',
                                       blank=True)
    converge = models.ForeignKey(BurrConverge, verbose_name='毛刺收敛', on_delete=models.CASCADE, null=True, blank=True)
    similar = models.ForeignKey('self', verbose_name='同类事件', on_delete=models.SET_NULL, null=True, blank=True)

    tags = TaggableManager(through=TaggedUUIDItem, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = '- 告警事件'

    def __str__(self):
        return self.name

    def get_similar(self):
        """
        查询同类事件，返回布尔值。因为是在已经创建事件完成之后再来判断，所以判断事件数量有两个。找到之后，更新similar 字段
        关联自身。用于区分后续同类事件不在发送通知的标记处理，同时也是压缩事件汇总过滤的关键参数。
        所有同类事件：Event.objects.filter(project=self.project, host=self.host, type=message.type)
        未关联相似事件：Event.objects.filter(project=self.project, host=self.host, type=message.type, similar=None)
        """
        # 查询同类事件的维度：项目、主机、类型
        # todo 使用 count 方法 for sh (不确定需求)
        # similar_event = Event.objects.filter(project=self.project, host=self.host, type=message.type)
        similar_event_count = Event.objects.filter(project=self.project, host=self.host, type=self.type,
                                                   status__in=STATUS_NOT_CLOSED).count()
        if similar_event_count >= 2:
            # 找到同类事件之后，similar字段判断该事件是否为重复, 为空则是新建时间，非空则是已有同类
            self.similar = self
            self.save()
            logger.debug("[debug] find similar count: %s" % similar_event_count)
            return True
        else:
            logger.debug("[debug] not found similar count: %s" % similar_event_count)
            return False

    def get_created_time(self):
        """ 获取事件创建的时间，数据库默认存的是UTC时间，该方法处理为北京时间"""
        cst_tz = timezone('Asia/Shanghai')
        cn_time = self.created.replace(tzinfo=cst_tz)
        return cn_time + timedelta(hours=8)

    def get_modified_time(self):
        """ 获取事件关联告警消息的最后一条修改时间来返回，数据库默认存的是UTC时间，该方法处理为北京时间"""
        cst_tz = timezone('Asia/Shanghai')
        modified_time = self.messages.last().modified
        cn_time = modified_time.replace(tzinfo=cst_tz)
        return cn_time + timedelta(hours=8)

    def get_receivers(self):
        """ 获取事件已经通知的人员信息"""
        receiver_list = [user.username for user in self.receivers.all()]
        return ','.join(receiver_list)



