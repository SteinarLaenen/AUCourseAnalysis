# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-07 12:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, null=True)),
                ('level', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fb_id', models.CharField(max_length=100)),
                ('date_posted', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reviewer', models.BooleanField(default=False)),
                ('fb_id', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=25)),
            ],
        ),
        migrations.AddField(
            model_name='review',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='reviews.User'),
        ),
        migrations.AddField(
            model_name='review',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reviews.Course'),
        ),
        migrations.AddField(
            model_name='review',
            name='likes',
            field=models.ManyToManyField(related_name='liked', to='reviews.User'),
        ),
        migrations.AddField(
            model_name='course',
            name='discipline',
            field=models.ManyToManyField(related_name='Discipline', to='reviews.Discipline'),
        ),
        migrations.AddField(
            model_name='course',
            name='theme',
            field=models.ManyToManyField(to='reviews.Theme'),
        ),
        migrations.AddField(
            model_name='course',
            name='track',
            field=models.ManyToManyField(to='reviews.Track'),
        ),
    ]
