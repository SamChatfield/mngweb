# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-31 15:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('faq', '0002_faqcategorypage_sort_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faqcategorypage',
            name='sort_order',
        ),
    ]