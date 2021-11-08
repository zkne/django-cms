# Generated by Django 1.11.14 on 2018-07-19 16:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('cms', '0022_auto_20180620_1551'),
    ]

    operations = [
        migrations.AddField(
            model_name='placeholder',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='placeholder',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
