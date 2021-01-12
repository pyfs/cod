from django.db import models
from event.models import Event
from utils.common.models import OwnerModel
from model_utils.models import TimeStampedModel, SoftDeletableModel, UUIDModel, TimeFramedModel
from project.models import Project


class Silence(UUIDModel, OwnerModel, TimeStampedModel, SoftDeletableModel, TimeFramedModel):
    """短期沉默规则"""
    project = models.ForeignKey(Project, verbose_name='项目名称', on_delete=models.CASCADE)
    # 关联事件获取里面关联的字段信息而非对象，例如event.type=CPU,这样可以基于事件类型进行收敛或者过滤
    type = models.ForeignKey(Event, verbose_name='关联事件', on_delete=models.CASCADE)
    ignore_type = models.BooleanField(verbose_name='忽略类型', default=False)

    class Meta:
        verbose_name_plural = verbose_name = '- 沉默规则'

    def __str__(self):
        return self.project.name
