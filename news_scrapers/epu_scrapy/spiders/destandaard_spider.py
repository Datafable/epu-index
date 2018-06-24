import json
import os
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
        start_url = 'http://www.standaard.be/zoeken/?keyword={0}&datestart={1}&dateend={2}'.format(term, yesterday_str, yesterday_str)
    else:
        start = datetime(*strptime(settings['period']['start'], '%Y-%m-%d')[:6]) # awkward syntax to convert struct time to datetime (see: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object)
        start_str = '{0}/{1}/{2}'.format(start.day, start.month, start.year)
        end = datetime(*strptime(settings['period']['end'], '%Y-%m-%d')[:6])
        end_str = '{0}/{1}/{2}'.format(end.day, end.month, end.year)
        start_url = 'http://www.standaard.be/zoeken/?keyword={0}&datestart={1}&dateend={2}'.format(term, start_str, end_str)
    return start_url


class DeStandaardSpider(Spider):
    name = 'standaard' # name of the spider, to be used when running from command line
    allowed_domains = ['www.standaard.be']
    _settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = ['http://www.standaard.be/account/logon']

    def parse(self, response):
        """
        Overwrites Spiders parse method. Fill in log in details in log in form and submit.
        :return:
        """
        print('custom settings:')
        print(self._settings)
        return FormRequest.from_response(
            response,
            formxpath='//div[contains(concat(" ", normalize-space(@class), " "), " main-container ")]/descendant::form',
            formdata={'EmailOrUsername': self._settings['username'], 'Password': self._settings['password']},
            callback=self.go_to_search_site
        )

    def go_to_search_site(self, response):
        """
        After login attempt, construct url to search page and start scraping that page by returning a Request object
        :return: Scrapy.Request object that will be parsed by parse_search_results.
        """
        if 'U heeft een ongeldig e-mailadres of wachtwoord ingevuld' in response.body.decode('utf-8'):
            raise CloseSpider('could not log on')
        else:
            url = set_start_url(self._settings)
            return Request(url, callback=self.parse_search_results)


    def date_within_settings_period(self, given_date):
        """
        check whether the given date is included in the period configured in the settings
        :return: True or False
        """
        if type(self._settings['period']) is not dict:
            today = date.today()
            end = datetime(today.year, today.month, today.day, 0, 0, 0)
            start = end - timedelta(days=1)
        else:
            start = datetime(*strptime(self._settings['period']['start'], '%Y-%m-%d')[:6])
            end = datetime(*strptime(self._settings['period']['end'], '%Y-%m-%d')[:6])
            end = end + timedelta(days=1) # the previous statement will set end to 00:00:00
        return given_date >= start and given_date <= end


    def article_published_in_period(self, article_element):
        """
        check whether the article is published within the period configured in the settings. De Standaard returns
        older articles in its search results so these need to be removed.
        :return: True or False
        """
        url = article_element.xpath('a/@href').extract()
        dates = article_element.xpath(
            'a/div[contains(concat(" ", normalize-space(@class), " "), " article__body ")]/time/text()'
        ).extract()
        if len(dates) > 0:
            date = dates[0]
        else:
            raise CloseSpider('Could not parse date from article: {0}'.format(url[0]))
        dt = datetime(*strptime(date, '%d/%m/%Y %H:%M:%S')[:6])
        return self.date_within_settings_period(dt)


    def parse_search_results(self, response):
        """
        Parse the search results page.
        :return: Scrapy.Request objects to next search results page and to article pages
        """
        # find next pages
        next_link = response.xpath('''
            //div[@data-mht-block="searchresults__searchresults"]
            /descendant::*
            /nav[contains(concat(" ", normalize-space(@class), " "), " pagination ")]
            /descendant-or-self::li[contains(concat(" ", normalize-space(@class), " "), " next-page ")]
            /a/@href
            ''').extract()
        if len(next_link) > 0:
            next_link = next_link[0]
            yield Request(next_link, callback=self.parse_search_results)

        # find regular articles
        article_elements = response.xpath('''
            //div[@data-mht-block="searchresults__searchresults"]
            /div
            /article[contains(concat(" ", normalize-space(@class), " "), " article-live ")]
        '''
        )
        # find DS+ articles (=> different class of the article element itself)
        dsplus_article_elements = response.xpath('''
            //div[@data-mht-block="searchresults__searchresults"]
            /div
            /article[contains(concat(" ", normalize-space(@class), " "), " article-archive ")]
        '''
        )
        for article_element in article_elements:
            url = article_element.xpath('a/@href').extract()[0]
            if self.article_published_in_period(article_element):
                yield Request(url, callback=self.parse_live_article)
            else:
                raise CloseSpider("article {0} is not in date range".format(url))
        for article_element in dsplus_article_elements:
            # if self.article_published_in_period(article_element):
            #     url = article_element.xpath('a/@href').extract()[0]
            #     yield Request(url, callback=self.parse_archive_article)
            pass  # JS rendering needed to parse archived articles


    def parse_archive_article(self, response):
        # search for article title
        title_parts = set(response.css('article div.DS-head header h1').xpath('./descendant-or-self::*/text()').extract())
        if len(title_parts) > 0:
            title = list(title_parts)[0].strip()
        else:
            title = ''

        # search for article published date
        publish_date_parts = response.xpath('//meta[@property="article:modified_time"]').extract()
        if len(publish_date_parts) == 0:
            datetime_str = ''
        else:
            publish_date_str = response.xpath('//meta[@property="article:modified_time"]').extract()[0]
            datetime_str = publish_date_str[0:10]

        # get article intro
        intro = ' '.join(
            [x.strip() for x in response.css('article div.DS-head header div.DS-introduction').xpath(
                './descendant-or-self::*/text()').extract()
            ]
        )

        # get article text
        article_text = ' '.join(
            [x.strip() for x in response.css('article div.DS-head').xpath(
                'string(./following-sibling::*)').extract()
             if x
             ]
        )

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = intro
        article['title'] = title
        article['published_at'] = datetime_str
        article['text'] = article_text
        return article

    def parse_live_article(self, response):
        # search for article title
        title_parts = response.xpath('''
            //div[contains(concat(" ", normalize-space(@class), " "), " main-container ")]
            /descendant::div[@data-mht-block="article-detail__article-header"]
            /descendant::header[contains(concat(" ", normalize-space(@class), " "), " article__header ")]
            /h1/text()
            '''
        ).extract()
        if len(title_parts) > 0:
            title = title_parts[0].strip()
        else:
            title = ''

        # search for article published date
        published_date_parts = response.xpath('''
            //div[contains(concat(" ", normalize-space(@class), " "), " main-container ")]
            /descendant::div[@data-mht-block="article-detail__article-header"]
            /descendant::footer[contains(concat(" ", normalize-space(@class), " "), " article__meta ")]
            /p/time/@datetime
            '''
        ).extract()
        if len(published_date_parts) > 0:
            datetime_str_with_tz = published_date_parts[0]  # datetime attribute is in iso format...
            datetime_str = datetime_str_with_tz[0:-7]  # ...but we'll drop the time zone information
        else:
            datetime_str = ''

        # get article div
        article_div = response.xpath('''
            //div[@data-mht-block="article-detail__article-body"]
            /descendant::article
            /div[contains(concat(" ", normalize-space(@class), " "), " article__body ")]
            '''
        )
        if len(article_div) > 0:
            article_div = article_div[0]
            # search for article intro text
            intro_parts = article_div.xpath('''
                div[contains(concat(" ", normalize-space(@class), " "), " intro ")]
                /descendant-or-self::*/text()
                '''
            ).extract()
            article_intro = ' '.join([x.strip() for x in intro_parts])

            # search for article full text
            text_parts = article_div.xpath('p/descendant-or-self::*/text()').extract()
            article_text = ' '.join([x.strip() for x in text_parts])
        else:
            article_intro = ''
            article_text = ''

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['published_at'] = datetime_str
        article['text'] = article_text
        return article
