# Generated by Django 2.2.14 on 2020-11-27 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('send_template', '0002_auto_20201125_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendtemplate',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(0, '告警'), (1, '恢复')], default=0, verbose_name='消息类型'),
        ),
    ]
