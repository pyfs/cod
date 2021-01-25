from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from model_utils.models import SoftDeletableModel, UUIDModel
from django.contrib.auth.models import BaseUserManager
from django.forms.models import model_to_dict
from account.avatar import IDAvatar
from utils.taggit.models import TaggedUUIDItem
from taggit.managers import TaggableManager


class UserManager(BaseUserManager):

    def _create_user(self, username, is_staff, is_superuser, **kwargs):
        if not username:
            raise ValueError('username 必须提供')
        user = self.model(username=username,
                          is_staff=is_staff,
                          is_superuser=is_superuser,
                          **kwargs)
        password = kwargs.get('password', None)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, **kwargs):
        return self._create_user(username=username, is_staff=False, is_superuser=False, **kwargs)

    def create_superuser(self, username, **kwargs):
        return self._create_user(username, is_staff=True, is_superuser=True, **kwargs)


class User(UUIDModel, SoftDeletableModel, AbstractUser):
    """自定义用户模型"""
    # 必填字段
    username = models.CharField(verbose_name='用户', max_length=40, unique=True)
    cn_name = models.CharField(verbose_name='中文名', max_length=20, blank=True, null=True)

    # 选填字段
    # 第三方登录创建账号时无需密码
    password = models.CharField(verbose_name='密码', max_length=128, blank=True, null=True)
    email = models.EmailField(verbose_name='邮箱', max_length=25, blank=True, null=True)
    mobile = models.CharField(verbose_name='手机', max_length=11, blank=True, null=True)
    avatar = models.CharField(verbose_name='头像', default=IDAvatar(email).wavatar(), max_length=200)
    qq = models.CharField(verbose_name='QQ号', max_length=32, blank=True, null=True)
    wx = models.CharField(verbose_name='微信', max_length=32, blank=True, null=True)

    # 额外用户状态字段，根据不同项目调整
    global_immunity = models.BooleanField(verbose_name='免扰模式', default=False)
    similar_block = models.BooleanField(verbose_name='同类阻断', default=False)
    signature = models.CharField(verbose_name='签名', max_length=200, blank=True, null=True)
    tags = TaggableManager(through=TaggedUUIDItem, blank=True)
    filter_types = models.TextField(verbose_name='规则类型', blank=True, null=True)

    # todo 配置型属性与功能型属性区分开 for jjj
    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'cn_name']

    objects = UserManager()

    class Meta:
        ordering = ['-date_joined']
        verbose_name_plural = verbose_name = '- 用户模型'

    def __str__(self):
        return self.username

    # todo 下面这两个方法导致 app account 无法独立使用，考虑讲方法迁移到 view 层 for sh （暂时不动）

    def get_channel(self) -> list:
        """
        获取用户关联的所有接收通道，数据库里面存放是对应的数字对应值, 映射列表查看receive_strategy/constants.py
        :return: 返回用户关联的所有通道，类型是：数字列表
        """
        return [rs.channel for rs in self.receivestrategy_set.all()]

    def get_silence_ignore_type(self):
        """ 基于用户查询关联的沉默规则，判断当前时间是否在star < now < end, 如果真则返回true"""
        #  查询数据库是此类日期格式会有异常，怀疑和sqlite3 存放数据有关系，存疑。
        # date_now = timezone.now()  # 2020-11-10 08:25:56.529617+00:00
        # date_now = datetime.now()  # 2020-11-10 16:25:56.959058
        ignore_type = False
        for silence in self.silence_set.all():
            if not silence.is_removed and silence.start < timezone.now() < silence.end:
                ignore_type = True
                break
            else:
                ignore_type = False
        return ignore_type

    def get_user_tags(self, tag_type='daily') -> list:
        """ 基于用户查询指定标签的内容 """
        tags_list = [tag.name for tag in self.tags.all()]
        tag_values_list = []
        for tag_str in tags_list:
            tag_key, tag_value = tag_str.split(':', 1)
            if tag_key == tag_type:
                tag_values_list.append(tag_value.strip())
        return tag_values_list

    def get_user_tagtype(self, tag_type='daily') -> bool:
        """ 查询用户设置中是否包含自定标签类型 """
        tags_list = [tag.name for tag in self.tags.all()]
        for tag_str in tags_list:
            tag_key, tag_value = tag_str.split(':', 1)
            if tag_key == tag_type:
                return True
        else:
            return False

    def get_user_project(self) -> list:
        """ 获取用户关联的项目 """

        charged_projects_list, subscribe_projects_list, belong_to_projects_list = [], [], []
        # 获取所负责的项目
        if self.charged_project.all():
            charged_projects_list = list(filter(lambda x: x.get_children().last() is None, self.charged_project.all()))

        # 获取订阅的项目
        if self.subscribe_project.all():
            subscribe_projects_list = list(filter(lambda x: x.get_children().last() is None, self.subscribe_project.all()))

        # 获取所属的项目
        if self.belong_to_project.all():
            belong_to_projects_list = list(filter(lambda x: x.get_children().last() is None, self.belong_to_project.all()))

        # 返回项目对象列表
        return list(set(charged_projects_list+subscribe_projects_list+belong_to_projects_list))
