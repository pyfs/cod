# Generated by Django 2.2.14 on 2020-11-24 02:29

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthToken',
            fields=[
                ('start', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('end', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('status', model_utils.fields.StatusField(choices=[('草稿', '草稿'), ('发布', '发布'), ('下架', '下架')], default='草稿', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('is_removed', models.BooleanField(default=False)),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, verbose_name='秘钥名称')),
                ('token', models.UUIDField(default=uuid.uuid4, verbose_name='认证秘钥')),
            ],
            options={
                'verbose_name': '- 密钥认证',
                'verbose_name_plural': '- 密钥认证',
                'ordering': ['owner__username'],
            },
        ),
    ]