from uuid import uuid4
from django.db import models
from utils.common.models import OwnerModel, DateTimeFramedModel
from model_utils.models import StatusModel, SoftDeletableModel, UUIDModel
from model_utils.choices import Choices
from utils.common.constants import STATUS_PUBLISHED, STATUS_DRAFT, STATUS_OFFLINE
from data_source.models import DataSource

# Create your models here.


class AuthToken(UUIDModel, OwnerModel, StatusModel, DateTimeFramedModel, SoftDeletableModel):
    """
    仿照 rest_framework.authtoken 自定义 token
    token 绑定 data_source 和 owner
    """
    STATUS = Choices(STATUS_DRAFT, STATUS_PUBLISHED, STATUS_OFFLINE)

    name = models.CharField(verbose_name='秘钥名称', max_length=50)
    token = models.UUIDField(verbose_name='认证秘钥', default=uuid4, max_length=32)
    data_source = models.ForeignKey(DataSource, verbose_name='数据源', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = verbose_name = '- 密钥认证'
        ordering = ['owner__username']

    def __str__(self):
        return "%s_%s" % (self.owner, self.name)
