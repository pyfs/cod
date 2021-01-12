from django.db import models
from model_utils.models import UUIDModel, SoftDeletableModel, TimeStampedModel, TimeFramedModel

from receive_strategy.constants import RECEIVE_CHOICES, WECHAT
from utils.common.models import OwnerModel, EnabledModel


class ReceiveStrategy(UUIDModel, OwnerModel, SoftDeletableModel, TimeStampedModel, TimeFramedModel, EnabledModel):
    # todo 测试 default 值问题
    channel = models.PositiveSmallIntegerField(verbose_name='接收通道', choices=RECEIVE_CHOICES, default=WECHAT)

    class Meta:
        verbose_name_plural = verbose_name = '- 接收策略'

    def __str__(self):
        return "%s" % self.channel
