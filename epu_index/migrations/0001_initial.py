# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EpuIndexScore',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('number_of_articles', models.IntegerField()),
                ('number_of_papers', models.IntegerField()),
                ('epu', models.FloatField()),
            ],
        ),
    ]
