# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0006_journalsscraped'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='journalsscraped',
            unique_together=set([('journal', 'date')]),
        ),
    ]
