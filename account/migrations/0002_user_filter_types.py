# Generated by Django 2.2.14 on 2020-12-11 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='filter_types',
            field=models.TextField(blank=True, null=True, verbose_name='规则类型'),
        ),
    ]