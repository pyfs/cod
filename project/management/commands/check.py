# encoding: utf-8
# __author__ = "liushenghua"
# Date: 2020/12/3
import argparse
import json
import os

from django.core.management import BaseCommand

from account.models import User
from event.models import Event
from project.models import Project


class Command(BaseCommand):
    help = 'init data for cmdb export json file.'

    def __init__(self):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Cod.settings')
        """加载文件数据"""
        super(Command, self).__init__()

    def add_arguments(self, parser):
        parser.add_argument('--no-receivers', nargs='+', type=str)
        parser.add_argument('--project-config', nargs='+', type=str)
        parser.add_argument('--person', nargs='+', type=str)

    @staticmethod
    def check_no_receivers(project_name):
        """ 检查项目所有事件里面，没有关联发送人员的事件，此类事件则是没有发送通知给到关联人员"""
        project = Project.objects.get(name=project_name)
        events = Event.objects.filter(project=project).order_by("created")
        print("*****************搜索项目里面事件没有关联接收人员的事件列表******************")
        for event in events:
            if not event.receivers.all():
                print('时间:{0}, 事件ID:{1}, 项目名称:{2}, 分派策略:{3}'.format(event.modified, event.id,
                                                                    event.project.name,
                                                                    project.delivery_set.all().last()))

    @staticmethod
    def check_projects_all_config(project_name=None):
        projects = []
        if project_name:
            projects.append(Project.objects.get(name=project_name))
        else:
            projects = Project.objects.filter().order_by("created")
        for project in projects:
            delivery = project.delivery_set.all().last()
            group = delivery.group.all().last()
            users = [user.username for user in group.user_set.all()]
            print("*****************搜索项目关联的所有组以及组关联用户******************")
            print('项目名称:{0}, 分配策略:{1}, 用户组:{2}, 用户列表:{3}'.format(project.name,
                                                                 delivery.name,
                                                                 group.name,
                                                                 users))

    @staticmethod
    def check_person_send_event(user_name, project):
        """
       以人的视角来查询发送的事件，只要人员信息在事件的接收关联列表里面
       """
        project = Project.objects.get(name=project)
        delivery_list = project.delivery_set.all()
        user = User.objects.get(username=user_name)
        groups_name = [group.name for group in user.groups.all()]
        events = Event.objects.filter(project=project).order_by("created")

        print("*****************搜索用户关联的所有组******************")
        print('用户:{0},关联的用户组:{1}'.format(user.username, groups_name))

        print("*****************搜索已经发送给到用户的关联事件******************")
        for event in events:
            if user in event.receivers.all():
                print('项目:{0},用户:{1},事件ID:{2},事件时间:{3},状态:"该事件已经发送给到用户".'.format(project.name,
                                                                                 user.username,
                                                                                 event.id,
                                                                                 event.modified))

    def handle(self, *args, **options):
        for project in options['no-receivers']:
            self.check_projects_all_config(project)
        for project in options['project-config']:
            self.check_no_receivers(project)
        # for user in options['person']:

        # print(options['max'])
        # if options["delete"]:
            # self.check_project_receivers('INFRA_CCLOUD')
            # print(args, options)

        # self.check_projects_all_config('INFRA_CCLOUD')
        # self.check_person_send_event('liushenghua', 'INFRA_CCLOUD')
