import os
import json
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from converge.models import BurrConverge
from delivery.models import Delivery
from event.models import Event
from project.models import Project
from account.models import User
from django.contrib.auth.models import Group

from utils.common.constants import STATUS_PUBLISHED


class Command(BaseCommand):
    help = 'init data for cmdb export json file.'

    def __init__(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cod.settings')
        """加载文件数据"""
        # self.cmdb_data = json.load(open(os.path.join(settings.BASE_DIR, 'FeHelper-20201124150956.json')))
        super(Command, self).__init__()

    def add_arguments(self, parser):
        parser.add_argument('--importproject', nargs='+', type=str)

    @staticmethod
    def get_user(user):
        try:
            return User.objects.get(username=user)
        except User.DoesNotExist:
            return User.objects.create(username=user)

    def create_project(self, project_name, user):
        """ 创建项目"""
        # 项目名字 格式 INFRA_CCLOUD
        # 获取产品线，产品的名字
        product_line_name, product_name = project_name.split('_')
        try:
            product_line = Project.objects.get(label=product_line_name)
            product_line.parent = None
            product_line.save()
        except Project.DoesNotExist:
            product_line = Project.objects.update_or_create(parent=None, name=product_line_name,
                                                            label=product_line_name,
                                                            pic=self.get_user(user),
                                                            owner=self.get_user(user))[0]

        # 创建产品
        try:
            product = Project.objects.get(label=product_name)
            product.parent = product_line
            product.save()
        except Project.DoesNotExist:
            product = Project.objects.update_or_create(parent=product_line, name=product_name,
                                                       label=product_name,
                                                       pic=self.get_user(user),
                                                       owner=self.get_user(user))[0]

        # 创建项目
        try:
            project = Project.objects.get(label=project_name)
            project.parent = product
            project.save()
        except Project.DoesNotExist:
            return Project.objects.update_or_create(parent=product, name=project_name,
                                                    label=project_name,
                                                    pic=self.get_user(user),
                                                    owner=self.get_user(user))

    def create_group(self, group_name, user):
        """ 创建用户组"""
        # 用户组 格式 INFRA_CCLOUD
        # 获取产品关联的主要负责人信息
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            group = Group.objects.create(name=group_name)
        # 用户关联组信息
        self.get_user(user).groups.add(group)

    def create_converge(self, project_name):
        # 项目名字project_name: 格式 INFRA_CCLOUD
        project = Project.objects.get(label=project_name)
        try:
            BurrConverge.objects.get(label=project_name)
        except BurrConverge.DoesNotExist:
            BurrConverge.objects.update_or_create(status=STATUS_PUBLISHED,
                                                  name=project_name,
                                                  project=project)

    def create_delivery(self, project_name, user):
        # 项目名字project_name: 格式 INFRA_CCLOUD
        # 获取产品关联的主要负责人信息 project_pic
        project = Project.objects.get(label=project_name)
        try:
            delivery = Delivery.objects.get(name=project_name)
        except Delivery.DoesNotExist:
            delivery = Delivery.objects.update_or_create(name=project_name, project=project,
                                                         owner=self.get_user(user))[0]

        delivery.group.add(Group.objects.get(name=project_name))

    def handle(self, *args, **options):
        # for data in self.cmdb_data:
        #     # 创建项目
        #     self.create_project(data)
        #     # 创建项目同名的用户组
        #     self.create_group(data)
        #     # 创建默认分派策略
        #     self.create_delivery(data)
        for value in options.keys():
            if value == 'importproject':
                project = options['importproject'][0]
                user = options['importproject'][1]
                # 基于项目创建产品线、产品、项目
                self.create_project(project, user)
                # 创建用户组
                self.create_group(project, user)
                # 创建分配策略
                self.create_delivery(project, user)
