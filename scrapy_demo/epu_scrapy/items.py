# -*- coding: utf-8 -*-

import scrapy


class Article(scrapy.Item):
    text = scrapy.Field()
    title = scrapy.Field()
    datetime = scrapy.Field()
