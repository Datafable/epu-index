# -*- coding: utf-8 -*-
from scrapy_djangoitem import DjangoItem
from epu_index.models import Article

class Article(DjangoItem):
    django_model = Article
