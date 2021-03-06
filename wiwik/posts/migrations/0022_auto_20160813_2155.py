# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-13 19:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0021_auto_20160813_1214'),
    ]

    operations = [
        migrations.RenameField(
            model_name='categories',
            old_name='text',
            new_name='topics',
        ),
        migrations.AddField(
            model_name='post',
            name='category',
            field=models.ForeignKey(default=0, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='posts.Categories'),
        ),
    ]
