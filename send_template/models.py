from django.db import models
from model_utils.models import UUIDModel, SoftDeletableModel, TimeStampedModel

from data_source.models import DataSource
from receive_strategy.constants import RECEIVE_CHOICES, WECHAT, TYPE_CHOICES, ALERT
from utils.common.models import EnabledModel


class SendTemplate(UUIDModel, SoftDeletableModel, TimeStampedModel, EnabledModel):
    name = models.CharField(verbose_name='模板名称', max_length=120)
    ds = models.ManyToManyField(DataSource, verbose_name='数据源', blank=True)
    channel = models.PositiveSmallIntegerField(verbose_name='接收通道', choices=RECEIVE_CHOICES, default=WECHAT)
    type = models.PositiveSmallIntegerField(verbose_name='消息类型', choices=TYPE_CHOICES, default=ALERT)
    content = models.TextField(verbose_name='模板内容')

    class Meta:
        verbose_name_plural = verbose_name = '- 发送模板'

    def __str__(self):
        return "%s" % self.channel
