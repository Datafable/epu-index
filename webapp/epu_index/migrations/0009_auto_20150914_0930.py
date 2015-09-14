# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0008_auto_20150817_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.URLField(unique=True, null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([]),
        ),
    ]
