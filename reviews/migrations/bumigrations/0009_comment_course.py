# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-08 15:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0008_remove_comment_course'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='course',
            field=models.ManyToManyField(to='reviews.Course'),
        ),
    ]
