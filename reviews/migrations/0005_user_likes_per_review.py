# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-21 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20171221_2007'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='likes_per_review',
            field=models.IntegerField(default=0),
        ),
    ]
