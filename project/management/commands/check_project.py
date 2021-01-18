from django.core.management import BaseCommand

from message.models import Message
from project.models import Project


class Command(BaseCommand):
    help = 'init data for cmdb export json file.'

    def add_arguments(self, parser):
        parser.add_argument('--msg', type=str)

    def handle(self, *args, **options):
        msg_id = options['msg']
        msg = Message.objects.get(pk=msg_id)
        project = Project.objects.get(label=msg.project)
        print('project', project)
        print('msg_project', msg.project)
