# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0010_auto_20150918_1259'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wordsperday',
            name='date',
            field=models.DateField(db_index=True),
        ),
    ]
