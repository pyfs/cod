from django.db import models
from model_utils.models import StatusModel, TimeStampedModel, SoftDeletableModel, UUIDModel
from model_utils.choices import Choices
from utils.common.constants import STATUS_PUBLISHED, STATUS_DRAFT, STATUS_OFFLINE
from taggit.managers import TaggableManager
from utils.taggit.models import TaggedUUIDItem
from utils.common.models import EnabledModel


# Create your models here.


class DataSource(UUIDModel, StatusModel, TimeStampedModel, SoftDeletableModel, EnabledModel):
    """数据源管理 todo EnabledModel 状态暂时未使用 """
    STATUS = Choices(STATUS_DRAFT, STATUS_PUBLISHED, STATUS_OFFLINE)
    name = models.CharField(verbose_name='数据源', max_length=50)
    label = models.CharField(verbose_name='标示符', max_length=50, unique=True)
    close_timeout = models.PositiveSmallIntegerField(verbose_name='超时关闭', default=360)

    tags = TaggableManager(through=TaggedUUIDItem, blank=True)

    class Meta:
        verbose_name_plural = verbose_name = '- 数据源管理'

    def __str__(self):
        return self.name
