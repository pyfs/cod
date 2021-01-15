import logging
from datetime import timedelta

from django.db import models
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel, StatusModel, UUIDModel
from taggit.managers import TaggableManager

from converge.models import BurrConverge
from event.constants import STATUS_NOT_CLOSED
from message.constants import LEVEL_CHOICES, LEVEL_WARNING, STATUS_ALERT, STATUS_RECOVER
from project.models import Project
from utils.common.models import ExtraModel
from utils.taggit.models import TaggedUUIDItem
from data_source.models import DataSource

logger = logging.getLogger('django')


class Message(UUIDModel, TimeStampedModel, StatusModel, ExtraModel):
    """
    @data_source: 由 token 推断而来
    """
    STATUS = Choices(STATUS_ALERT, STATUS_RECOVER)
    project = models.CharField(verbose_name='项目标识', max_length=50)
    data_source = models.CharField(verbose_name='数据源', max_length=50, blank=True, null=True)
    type = models.CharField(verbose_name='消息标识', max_length=128)
    host = models.CharField(verbose_name='主机标识', max_length=128)
    title = models.CharField(verbose_name='消息标题', max_length=128)
    level = models.PositiveSmallIntegerField(verbose_name='消息等级', choices=LEVEL_CHOICES, default=LEVEL_WARNING)

    tags = TaggableManager(through=TaggedUUIDItem, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = '- 消息管理'
        ordering = ['-created']

    def __str__(self):
        return self.title

    def get_burr_converges(self):
        """ 查询消息项目关联的所有毛刺收敛规则，返回列表格式"""
        converges = BurrConverge.objects.filter(project=self.get_project(), is_removed=0).order_by(
            'modified')
        if not converges:
            logger.warning('host:{} no converge rule.'.format(self.host))
        return converges

    def get_data_source(self) -> object:
        """
        查询消息关联的数据源
        """
        return DataSource.objects.get(label=self.data_source.lower())

    def get_project(self) -> Project:
        """ 获取消息关联的项目"""
        return Project.objects.get(label=self.project)

    def get_burr_messages(self, burr_converge) -> list:
        """ 基于毛刺收敛规则查询到区间内的所有同类消息"""
        converge_time = self.modified - timedelta(minutes=burr_converge.section)  # 计算收敛区间值的时间格式
        # 基于毛刺收敛规则设置的时间区间，匹配所有告警消息
        return Message.objects.filter(project=self.project, host=self.host, type=self.type,
                                      created__lte=self.modified, created__gte=converge_time, ).order_by('level')

    def last_event(self) -> object:
        """ 基于消息查看是否有同类未关闭的事件，用于合并告警消息到已知事件"""
        from event.models import Event
        # 基于消息的关键信息查询是否存在同类事件，字段：主机、项目、类型、数据源、未关闭事件、未关联事件
        return Event.objects.filter(host=self.host, type=self.type,
                                    project=self.get_project(), ds=self.get_data_source(),
                                    status__in=STATUS_NOT_CLOSED, similar=None).order_by('created').last()
