# Generated by Django 2.2.14 on 2021-01-25 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_user_signature'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cn_name',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='中文名'),
        ),
    ]
