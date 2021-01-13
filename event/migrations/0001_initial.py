# Generated by Django 2.2.14 on 2020-11-24 02:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('converge', '0001_initial'),
        ('delivery', '0001_initial'),
        ('data_source', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('start', models.DateTimeField(blank=True, null=True, verbose_name='start')),
                ('end', models.DateTimeField(blank=True, null=True, verbose_name='end')),
                ('status', model_utils.fields.StatusField(choices=[('NO_RESPONSE', 'NO_RESPONSE'), ('PROCESSING', 'PROCESSING'), ('RESOLVED', 'RESOLVED'), ('REVOKED', 'REVOKED'), ('TIMEOUT', 'TIMEOUT')], default='NO_RESPONSE', max_length=100, no_check_for_status=True, verbose_name='status')),
                ('status_changed', model_utils.fields.MonitorField(default=django.utils.timezone.now, monitor='status', verbose_name='status changed')),
                ('is_removed', models.BooleanField(default=False)),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('extra', models.TextField(blank=True, null=True, verbose_name='额外数据')),
                ('name', models.CharField(max_length=120, verbose_name='事件名称')),
                ('host', models.CharField(max_length=128, verbose_name='主机标识')),
                ('level', models.PositiveSmallIntegerField(choices=[(0, '警告'), (1, '危险'), (2, '灾难')], default=0, verbose_name='事件级别')),
                ('type', models.CharField(max_length=50, verbose_name='事件类型')),
                ('converge', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='converge.BurrConverge', verbose_name='毛刺收敛')),
                ('current_delivery', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='delivery.Delivery', verbose_name='分派策略')),
                ('ds', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_source.DataSource', verbose_name='数据源')),
            ],
            options={
                'verbose_name': '- 告警事件',
                'verbose_name_plural': '- 告警事件',
            },
        ),
    ]