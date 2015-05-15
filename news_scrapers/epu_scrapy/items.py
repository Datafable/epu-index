# -*- coding: utf-8 -*-

import scrapy


class Article(scrapy.Item):
    intro = scrapy.Field()
    text = scrapy.Field()
    title = scrapy.Field()
    datetime = scrapy.Field()
    url = scrapy.Field()
