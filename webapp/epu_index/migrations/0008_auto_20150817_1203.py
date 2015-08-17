# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0007_auto_20150817_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='epuindexscore',
            name='date',
            field=models.DateField(unique=True),
        ),
    ]
