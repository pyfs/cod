import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from message.models import Message
from message.tasks import message_handler

logger = logging.getLogger('django')


@receiver(post_save, sender=Message)
def handler_message_post_save(sender, instance, **kwargs):
    created = kwargs.get('created')
    if created:
        message_handler.apply_async(args=[instance.id])
        logger.info('[!] handler message post save: %s' % instance.title)
