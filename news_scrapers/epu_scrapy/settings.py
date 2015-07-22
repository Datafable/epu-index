# -*- coding: utf-8 -*-
#     http://doc.scrapy.org/en/latest/topics/settings.html
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
webapp_dir = os.path.join(project_root, 'webapp')
sys.path.append(webapp_dir)
os.environ['DJANGO_SETTINGS_MODULE'] = 'webapp.settings'

BOT_NAME = 'epu_scrapy'

SPIDER_MODULES = ['epu_scrapy.spiders']
NEWSPIDER_MODULE = 'epu_scrapy.spiders'

ITEM_PIPELINES = {
    'epu_scrapy.pipelines.EpuScrapyPipeline': 100
}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'epu_scrapy (+http://www.yourdomain.com)'
