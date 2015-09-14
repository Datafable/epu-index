import json
import os
import re
from scrapy import Spider, FormRequest, Request
from scrapy.exceptions import CloseSpider
from epu_scrapy.items import Article
from datetime import datetime, timedelta, date
from time import strptime

def set_start_url(settings):
    """
    Based on the dates given in the settings file, construct the start urls for the spider
    """
    term = settings['term']
    if type(settings['period']) is not dict:
        today = datetime.today()
        if settings['period'] != 'yesterday':
            raise CloseSpider("unknown period setting {0}. See the scrapers README for more information.".format(str(settings['period'])))
        yesterday = today - timedelta(days=1)
        yesterday_str = '{0}/{1}/{2}'.format(yesterday.day, yesterday.month, yesterday.year)
        start_url = 'http://zoeken.tijd.be/results?query={0}&datefrom={1}&dateuntil={2}'.format(term, yesterday_str, yesterday_str)
    else:
        start = datetime(*strptime(settings['period']['start'], '%Y-%m-%d')[:6]) # awkward syntax to convert struct time to datetime (see: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object)
        start_str = '{0}/{1}/{2}'.format(start.day, start.month, start.year)
        end = datetime(*strptime(settings['period']['end'], '%Y-%m-%d')[:6])
        end_str = '{0}/{1}/{2}'.format(end.day, end.month, end.year)
        start_url = 'http://zoeken.tijd.be/results?query={0}&datefrom={1}&dateuntil={2}'.format(term, start_str, end_str)
    return start_url

class DeTijdSpider(Spider):
    name = 'detijd' # name of the spider, to be used when running from command line
    allowed_domains = ['tijd.be']
    settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = ['http://diensten.tijd.be']

    def __init__(self):
        self.months = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december']

    def parse(self, response):
        """
        Overwrites Spiders parse method. Fill in log in details in log in form and submit.
        :return: FormRequest
        """
        return FormRequest.from_response(
            response,
            formxpath='//form[@id="fb_loginform"]',
            formdata={'username': self.settings['username'], 'password': self.settings['password']},
            callback=self.go_to_search_site
        )


    def go_to_search_site(self, response):
        """
        After login attempt, construct url to search page and start scraping that page by returning a Request object
        :return: Scrapy.Request object that will be parsed by parse_search_results.
        """
        if 'Gebruiker niet gevonden' in response.body:
            raise CloseSpider('could not log on')
        else:
            url = set_start_url(self.settings)
            return Request(url, callback=self.parse_search_results)


    def parse_search_results(self, response):
        """
        Parse the search results page.
        :return: Scrapy.Request objects to next search results page and to article pages
        """
        # find next pages
        next_link = response.xpath('''
            //div[@id="maincontent"]
            /descendant::div[
                contains(concat(" ", normalize-space(@class), " "), " article ")
                and contains(concat(" ", normalize-space(@class), " "), " grid2 ")
            ]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " pager ")]
            /ul
            /li[
                contains(concat(" ", normalize-space(@class), " "), " next ")
                and not(contains(concat(" ", normalize-space(@class), " "), " inactive "))
            ]
            /a/@href
            ''').extract()
        if len(next_link) > 0:
            next_link = next_link[0].encode('utf-8')
            yield Request(next_link, callback=self.parse_search_results)
        else:
            print 'no next page to parse'

        # find articles
        article_urls = response.xpath('''
            //div[@id="maincontent"]
            /descendant::div[
                contains(concat(" ", normalize-space(@class), " "), " article ")
                and contains(concat(" ", normalize-space(@class), " "), " grid2 ")
            ]
            /descendant::div[@id="resultlist"]
            /div[contains(concat(" ", normalize-space(@class), " "), " result ")]
            /div[contains(concat(" ", normalize-space(@class), " "), " snippet ")]
            /a/@href
        '''
        ).extract()

        # in contrast to destandaard spider, detijd spider will not check whether the returned articles are indeed
        # published during the period specified in the crawling settings file.
        # De Standaard returns *additional* articles to the users provided date range. De Tijd however, has a timezone
        # issue: in summer (when the local time is UTC+02) articles published before 02:00:00 in the morning are
        # returned when you query the previous day, but they are not included when you query the current day. So if we
        # would strip these articles - like we do for De Standaard - then we lose them.
        for article_url in article_urls:
            yield Request(article_url, callback=self.parse_article)


    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('''
            //div[contains(concat(" ", normalize-space(@class), " "), " js-article-body ")]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__title-container ")]
            /h1[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__title ")]
            /text()
            '''
        ).extract()
        if len(title_parts) > 0:
            # the character that is replaced is a soft newline. It is used to mark places in words where you can cut them
            # should you need to wrap the text to the next line. All text is full of these characters so we strip them.
            title = title_parts[0].strip().encode('utf-8').replace('\xc2\xad', '')
        else:
            title = ''

        # search for article published date
        published_date_parts = response.xpath('''
            //div[contains(concat(" ", normalize-space(@class), " "), " l-grid--article-page ")]
            /descendant::li[
                contains(concat(" ", normalize-space(@class), " "), " m-meta__item ")
                and contains(concat(" ", normalize-space(@class), " "), " date ")
            ]
            /descendant::span[contains(concat(" ", normalize-space(@class), " "), " m-meta__item__text ")]
            '''
        ).extract()
        if len(published_date_parts) > 0:
            datetime_str = published_date_parts[0].encode('utf-8') # datetime attribute is in iso format
            m = re.search('(?P<day>\d+)\s+(?P<month>\w+)\s+(?P<year>\d+)\s+(?P<hours>\d+):(?P<minutes>\d+)', datetime_str)
            if m:
                day = int(m.group('day'))
                month = self.months.index(m.group('month')) + 1
                year = int(m.group('year'))
                hours = int(m.group('hours'))
                minutes = int(m.group('minutes'))
                datetime_iso = datetime(year, month, day, hours, minutes)
                datetime_iso_str = datetime_iso.isoformat()
        else:
            datetime_iso_str = ''

        # search for article intro text
        intro_parts = response.xpath('''
            //div[contains(concat(" ", normalize-space(@class), " "), " js-article-body ")]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__container__table ")]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__article ")]
            /descendant::p[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__intro ")]
            /descendant-or-self::*/text()
            '''
        ).extract()
        article_intro = ' '.join([x.strip().encode('utf-8').replace('\xc2\xad', '') for x in intro_parts])
        article_intro = article_intro.strip()

        # search for article full text
        text_parts = response.xpath('''
            //div[contains(concat(" ", normalize-space(@class), " "), " js-article-body ")]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__container__table ")]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__article ")]
            /descendant::div[contains(concat(" ", normalize-space(@class), " "), " l-main-container-article__body ")]
            /descendant-or-self::*/text()
            '''
        ).extract()
        # text is returned as unicode, so this time, the soft-hyphen is u'\u00AD'
        article_text = ' '.join([x.strip().replace(u'\u00AD', '') for x in text_parts])
        article_text = article_text.strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['published_at'] = datetime_iso_str
        article['text'] = article_text
        if article['text'] != '':
            return article
