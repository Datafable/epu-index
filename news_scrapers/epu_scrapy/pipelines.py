# -*- coding: utf-8 -*-
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from epu_index.models import NewsJournal, JournalsScraped
from django.db import IntegrityError
import datetime
import json
import os
import re
import pandas as pd

class EpuScrapyPipeline(object):
    def open_spider(self, spider):
        settingsfile = os.path.join(os.path.dirname(__file__), 'crawling_settings.json')
        settings = json.load(open(settingsfile))
        self.journals = {j.spider_name: j for j in NewsJournal.objects.all()}
        self.word_weights = self._read_model_file(os.path.join(os.path.dirname(settingsfile), settings['model_file']))

    def close_spider(self, spider):
        js = JournalsScraped(journal=self.journals[spider.name], date=datetime.datetime.now().date())
        js.save()

    def process_item(self, item, spider):
        item['news_journal'] = self.journals[spider.name]
        if item['text'] != '':
            item['cleaned_text'] = self._clean_text(item['text'])
            item['epu_score'] = self._score_text(item['cleaned_text'])
        try:
            item.save()
        except IntegrityError, e:
            # article should be unique. This prevents us from inserting duplicate articles
            print '===> could not insert: <==='
            print e.message
        return item

    def _clean_text(self, intext):
        return ' '.join(re.findall('\w+', intext, flags=re.UNICODE)).encode('utf-8')

    def _read_model_file(self, filename):
        return pd.read_csv(filename, header=0, index_col=0)

    def _score_text(self, text):
        score = 0
        for word in text.split(' '):
            if word.lower() in self.word_weights.index:
                score += self.word_weights.loc[word.lower()]['weight']
        return score

