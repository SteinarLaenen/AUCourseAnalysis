# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-08 13:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20171208_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='fb_id',
            field=models.CharField(default=b'', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='fb_id',
            field=models.CharField(default=b'', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='fb_id',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
