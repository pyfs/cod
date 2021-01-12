from django.apps import AppConfig


class MessageConfig(AppConfig):
    name = 'message'
    verbose_name = '消息管理'

    def ready(self):
        from message import signals
