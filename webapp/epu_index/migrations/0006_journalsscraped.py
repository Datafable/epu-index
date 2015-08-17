# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0005_auto_20150803_0953'),
    ]

    operations = [
        migrations.CreateModel(
            name='JournalsScraped',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('journal', models.ForeignKey(to='epu_index.NewsJournal')),
            ],
        ),
    ]
