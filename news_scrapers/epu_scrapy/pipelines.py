# -*- coding: utf-8 -*-
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from epu_index.models import NewsJournal

class EpuScrapyPipeline(object):
    def open_spider(self, spider):
        self.journals = {j.spider_name: j for j in NewsJournal.objects.all()}

    def process_item(self, item, spider):
        item['news_journal'] = self.journals[spider.name]
        item.save()
        return item
