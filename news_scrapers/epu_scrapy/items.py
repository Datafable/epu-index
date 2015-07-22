# -*- coding: utf-8 -*-
from scrapy.contrib.djangoitem import DjangoItem
from epu_index.models import Article

class Article(DjangoItem):
    django_model = Article
