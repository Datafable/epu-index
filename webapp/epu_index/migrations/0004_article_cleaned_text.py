# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epu_index', '0003_auto_20150723_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='cleaned_text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
