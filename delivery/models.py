import re

from django.contrib.auth.models import Group
from django.db import models
from model_utils.models import UUIDModel, SoftDeletableModel, TimeStampedModel
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from django.conf import settings
from project.models import Project
from utils.common.models import OwnerModel
import logging

logger = logging.getLogger('django')


class Delivery(MPTTModel, UUIDModel, OwnerModel, SoftDeletableModel, TimeStampedModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(verbose_name='组名称', max_length=50)
    project = models.ForeignKey(Project, verbose_name='所属项目', on_delete=models.CASCADE)
    group = models.ManyToManyField(Group, verbose_name='通知组', blank=True)
    receivers = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name='通知用户', blank=True,
                                       related_name='receiver_delivery')
    delay = models.PositiveSmallIntegerField(verbose_name='延迟时间', default=15)
    upgrade_level = models.CharField(verbose_name='升级状态', max_length=50, blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = verbose_name = '- 分派策略'

    def __str__(self):
        return "%s" % self.name

    def get_users(self) -> list:
        """
        分配策略关联的用户和组，多对多关系反查所有的通知用户和组，然后遍历里面关联的成员，最后返回用户的对象列表
        """
        users_obj = []
        # 遍历所有关联的组
        for group in self.group.all():
            for user_object in group.user_set.all():
                # 遍历组中的成员
                users_obj.append(user_object)
                logger.debug('{{"u_id":"{0}","action":"get_users() 通过分配策略获取所有关联组的用户列表{1}"}}'
                             ''.format(user_object.id, user_object.username))
        # 获取订阅项目的干系人
        for receiver in self.receivers.all():
            if receiver not in users_obj:
                users_obj.append(receiver)
                logger.debug('{{"u_id":"{0}","action":"get_users() 通过分配策略获取所有通知的订阅用户列表{1}"}}'
                             ''.format(user_object.id, user_object.username))
        return users_obj

    def get_upgrade_level(self, event_level):
        """ 获取告警升级状态，判断事件的告警等级，是否需要升级"""
        if self.upgrade_level:
            if isinstance(self.upgrade_level, int) and event_level >= self.upgrade_level:
                return True
            # 判断多种升级状态
            if isinstance(self.upgrade_level, str) and re.search(r',', self.upgrade_level):  # 要求字符里面逗号分隔

                if event_level in self.upgrade_level.split(','):  # 判断
                    return True
                else:
                    return False
        else:
            return True


