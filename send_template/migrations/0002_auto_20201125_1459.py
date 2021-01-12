# Generated by Django 2.2.14 on 2020-11-25 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_source', '0001_initial'),
        ('send_template', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sendtemplate',
            name='ds',
            field=models.ManyToManyField(blank=True, to='data_source.DataSource', verbose_name='数据源'),
        ),
        migrations.AddField(
            model_name='sendtemplate',
            name='name',
            field=models.CharField(default='', max_length=120, verbose_name='模板名称'),
            preserve_default=False,
        ),
    ]
