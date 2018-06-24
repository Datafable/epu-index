import json
import os
import re
import requests
from scrapy import Spider, FormRequest, Request
from scrapy.exceptions import CloseSpider
from epu_scrapy.items import Article
from datetime import datetime, timedelta
from time import strptime


def set_start_url(settings, page=1):
    """
    Based on the dates given in the settings file, construct the start urls for the spider
    """
    term = settings['term']
    if type(settings['period']) is not dict:
        today = datetime.today()
        if settings['period'] != 'yesterday':
            raise CloseSpider("unknown period setting {0}. See the scrapers README for more information.".format(str(settings['period'])))
        yesterday = today - timedelta(days=1)
        yesterday_str = yesterday.isoformat()
        start_url = 'https://api.tijd.be/services/search/article?q={0}&page=1&pageSize=20&lang=nl&startDate={1}&endDate={2}'.format(term, yesterday_str, yesterday_str)
    else:
        start = datetime(*strptime(settings['period']['start'], '%Y-%m-%d')[:6]) # awkward syntax to convert struct time to datetime (see: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object)
        start_str = start.isoformat()
        end = datetime(*strptime(settings['period']['end'], '%Y-%m-%d')[:6])
        end_str = end.isoformat()
        start_url = 'https://api.tijd.be/services/search/article?q={0}&page={3}&pageSize=20&lang=nl&startDate={1}&endDate={2}'.format(term, start_str, end_str, page)

    return start_url


class DeTijdSpider(Spider):
    name = 'detijd' # name of the spider, to be used when running from command line
    allowed_domains = ['tijd.be']
    _settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = ['http://www.tijd.be/mijn-diensten']

    def __init__(self):
        self.months = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']

    def start_requests(self):
        """
        After login attempt, construct url to search page and start scraping that page by returning a Request object
        :return: Scrapy.Request object that will be parsed by parse_search_results.
        """
        r = requests.post('http://www.tijd.be/registration/postchoice',
                          data={'email': 'ellen_tobback@hotmail.com', 'currentFlowDefinition': 'registration-x-bots',
                                'currentFlowState': 'CHOICE_STATE', 'bumpReason': '', 'currentReturnUrl': '/logout',
                                'currentFlowBumpContext': 'ARTICLE', 'registrationSourceLabel': 'website'})

        r2 = requests.post('http://www.tijd.be/registration/postlogin',
                           data={'email': 'ellen_tobback@hotmail.com', 'currentFlowDefinition': 'registration-x-bots',
                                 'password': 'projectEPU', 'stayLoggedIn': 'true', '_stayLoggedIn': 'on',
                                 'currentFlowState': 'CHOICE_STATE', 'bumpReason': '',
                                 'currentReturnUrl': '/mijn-diensten', 'currentFlowBumpContext': 'ARTICLE',
                                 'registrationSourceLabel': 'website'
                                 })

        if 'r16-form__errormessage' in r2.text:
            raise CloseSpider('could not log on')
        else:
            url = set_start_url(self._settings)
            yield Request(url, callback=self.parse_search_results)

    def parse_search_results(self, response):
        """
        Parse the search results page.
        :return: Scrapy.Request objects to next search results page and to article pages
        """
        data = json.loads(response.body_as_unicode())
        # find next pages
        if data['pageSize'] * data['currentPage'] < data['total']:
            url = set_start_url(self._settings, data['currentPage'] + 1)
            yield Request(url, callback=self.parse_search_results)

        for article in data['results']:
            yield Request(article['url'], callback=self.parse_article)


    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('''
            //article//header/h1/text()
            '''
        ).extract()
        if len(title_parts) > 0:
            # the character that is replaced is a soft newline. It is used to mark places in words where you can cut them
            # should you need to wrap the text to the next line. All text is full of these characters so we strip them.
            title = title_parts[0].strip().replace('\xc2\xad', '')
        else:
            title = ''

        # search for article published date
        published_date_parts = response.xpath('''
            //article//header//time[@itemprop='datePublished']/@datetime
            '''
        ).extract()
        date_str = ''.join(published_date_parts)
        pub_date = datetime.strptime(date_str, '%Y-%m-%d %H:%M')

        # search for article intro text
        intro_selector = response.css('div.o-articlebody div.ac_paragraph--first')
        intro_parts = intro_selector.xpath('./descendant-or-self::*/text()').extract()
        article_intro = ' '.join([x.strip() for x in intro_parts])
        article_intro = article_intro.strip()

        # search for article full text
        text_parts = intro_selector.xpath('./following-sibling::div[not(contains(concat(" ", normalize-space(@class), " "), "ac_paragraph--first"))]/descendant-or-self::*/text()').extract()
        article_text = ' '.join([x.strip() for x in text_parts])
        article_text = article_text.strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['published_at'] = pub_date.isoformat()
        article['text'] = article_text
        if article['text'] != '':
            return article
