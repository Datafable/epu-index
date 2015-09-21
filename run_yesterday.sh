#!/usr/bin/sh

cd news_scrapers/epu_scrapy
python run_yesterday.py

cd ../../webapp
python cache_and_check_yesterday.py