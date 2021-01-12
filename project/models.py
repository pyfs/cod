from django.conf import settings
from django.db import models
from model_utils.models import StatusModel, TimeStampedModel, SoftDeletableModel, UUIDModel
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager

from utils.common.models import OwnerModel
from utils.taggit.models import TaggedUUIDItem


class Project(MPTTModel, UUIDModel, OwnerModel, SoftDeletableModel, TimeStampedModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(verbose_name='名称', max_length=50)
    label = models.CharField(verbose_name='标识', max_length=50, unique=True)
    pic = models.ForeignKey(settings.AUTH_USER_MODEL,
                            verbose_name='责任人',
                            on_delete=models.CASCADE,
                            related_name='charged_project')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     blank=True,
                                     verbose_name='成员',
                                     related_name='belong_to_project')
    subscribers = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                         blank=True,
                                         verbose_name='订阅',
                                         related_name='subscribe_project')
    filter_types = models.TextField(verbose_name='合并类型', blank=True, null=True)
    converge_status = models.BooleanField(verbose_name='开启收敛', default=False)

    tags = TaggableManager(through=TaggedUUIDItem, blank=True)

    class MPTTMeta:
        order_insertion_by = ['id']

    class Meta:
        verbose_name_plural = verbose_name = '- 项目管理'

    def __str__(self):
        return "%s" % self.name
