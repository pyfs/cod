# Generated by Django 2.2.14 on 2020-11-24 02:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '0001_initial'),
        ('delivery', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='delivery',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='所属项目'),
        ),
        migrations.AddField(
            model_name='delivery',
            name='receivers',
            field=models.ManyToManyField(blank=True, related_name='receiver_delivery', to=settings.AUTH_USER_MODEL, verbose_name='通知用户'),
        ),
    ]
