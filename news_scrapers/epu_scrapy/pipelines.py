# -*- coding: utf-8 -*-
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from epu_index.models import NewsJournal
from django.db import IntegrityError
import json
import os
import re

class EpuScrapyPipeline(object):
    def open_spider(self, spider):
        settings = json.load(open(os.path.join(os.path.dirname(__file__), 'crawling_settings.json')))
        self.journals = {j.spider_name: j for j in NewsJournal.objects.all()}
        # self.word_weights = self._read_model_file(settings['model_file'])

    def process_item(self, item, spider):
        item['news_journal'] = self.journals[spider.name]
        if item['text'] != '':
            item['cleaned_text'] = self._clean_text(item['text'])
        # item['epu_score'] = self._score_text(item['cleand_text'])
        try:
            item.save()
        except IntegrityError, e:
            # article should be unique. This prevents us from inserting duplicate articles
            print '===> could not insert: <==='
            print e.message
        return item

    def _clean_text(self, intext):
        return ' '.join(re.findall('\w+', intext, flags=re.UNICODE)).encode('utf-8')

    def _read_classifier_model(self, filename):
        # read csv. Could be as pandas dataframe with words as index
        return {'test': 0.4, 'economie': 1.4} # TODO: Replace with real model data

    def _score_text(self, text):
        score = 0
        for word in re.findall('\w', text): # TODO: Replace with real pattern
            if word.lower() in self.word_weights.keys():
                score += self.word_weights[word.lower()]
        return score

