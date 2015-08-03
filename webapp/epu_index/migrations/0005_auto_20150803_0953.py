# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0004_article_cleaned_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('news_journal', 'published_at', 'title')]),
        ),
    ]
