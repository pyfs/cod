# Generated by Django 2.2.14 on 2020-11-24 02:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiveStrategy',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('start', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('end', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('is_removed', models.BooleanField(default=False)),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_enabled', models.BooleanField(default=False, verbose_name='启用')),
                ('channel', models.PositiveSmallIntegerField(choices=[(1, '企业微信'), (2, '邮箱'), (3, '短信'), (4, '电话'), (0, '微信直通')], default=1, verbose_name='接收通道')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='作者')),
            ],
            options={
                'verbose_name': '- 接收策略',
                'verbose_name_plural': '- 接收策略',
            },
            managers=[
                ('timeframed', django.db.models.manager.Manager()),
            ],
        ),
    ]
