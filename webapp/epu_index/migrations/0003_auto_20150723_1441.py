# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0002_article'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsJournal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('spider_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='article',
            name='epu_score',
            field=models.DecimalField(null=True, max_digits=9, decimal_places=5, blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='intro',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='article',
            name='news_journal',
            field=models.ForeignKey(to='epu_index.NewsJournal', null=True),
        ),
    ]
