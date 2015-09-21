# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0009_auto_20150914_0930'),
    ]

    operations = [
        migrations.CreateModel(
            name='WordsPerDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('word', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('frequency', models.IntegerField()),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='wordsperday',
            unique_together=set([('word', 'date')]),
        ),
    ]
