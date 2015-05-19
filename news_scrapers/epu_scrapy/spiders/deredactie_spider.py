import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from epu_scrapy.items import Article
from datetime import datetime, timedelta
from time import strptime

class DeredactieSpider(CrawlSpider):
    name = 'deredactie' # name of the spider, to be used when running from command line
    allowed_domains = ['www.deredactie.be']
    today = datetime.today()
    search_day = today - timedelta(days=1) # search for articles of yesterday
    search_day_str = '{0}/{1}/{2}'.format(today.day, today.month, today.year)
    start_urls = ['http://deredactie.be/cm/vrtnieuws/1.516538?text=economie&type=text&range=atdate&isdate={0}&sort=date&action=submit&advancedsearch=on'.format(search_day_str)]

    def parse(self, response):
        """
        Parse the first search page to determine the number of articles returned. Use the urls offset parameter
        to iterate over all response pages and yield scrapy.Request objects that will be parsed with the
        parse_list_page function
        """
        nr_of_articles_element = response.xpath('//li[contains(concat(" ", normalize-space(@class), " "), " searchcounter ")]/text()').extract()
        if len(nr_of_articles_element) is 1:
            nr_of_articles = int(re.findall('[0-9]+', nr_of_articles_element[0].encode('utf-8'))[0])
            for i in range(0, nr_of_articles, 20):
                yield scrapy.Request(self.start_urls[0] + '&offset={0}'.format(i), callback=self.parse_list_page)
        else:
            raise scapy.CloseSpider("could not parse number of articles from {0}".format(response.url))



    def parse_published_datetime(self, datetime_element_parts):
        """
        Helper method to parse a datetime from a html element
        """
        datetime_str_parts = [x.encode('utf-8') for x in datetime_element_parts.xpath('text()').extract()]
        datetime_str = ' '.join(datetime_str_parts).strip()
        datetime_str_stripped = re.findall('[0-9]+/[0-9]+/[0-9]+[^0-9]+[0-9]+:[0-9]+', datetime_str)[0]
        dt = strptime(datetime_str_stripped, '%d/%m/%Y - %H:%M')
        datetime_iso_str = dt.strftime('%Y-%m-%d %H:%M')
        return datetime_iso_str


    def parse_list_page(self, response):
        """
        Parse a single page returned by the search query. Find all links referring to articles and yield
        scrapy.Request objects for every link found. The parsing of these links is done by the parse_article
        function.
        """
        print 'CUSTOM OUTPUT: page: {0}'.format(self.page)
        print response.url
        links = response.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " searchresults ")]/descendant::a/@href').extract()
        link_set = set([x.encode('utf-8') for x in links])
        for l in link_set:
            if l is not '#':
                if l [0] == '/':
                    l = 'http://deredactie.be' + l
                yield scrapy.Request(l, callback=self.parse_article)


    def parse_article(self, response):
        """
        De redactie uses single article pages and storyline pages. The difference can be determined by
        examining the url. If it contains the parameter '?eid=<some number>', then this page contains
        a storyline. A storyline consists of several related articles. The article that the search page
        was pointing to is captured in a html element with the id that is pointed to by the '?eid' url
        paramater.
        The parsing of storyline pages and single article pages is done by two distinct functions:
        parse_article_from_storyline and parse_single_article_page.
        """
        match = re.search('\?eid=([0-9.]+)', response.url)
        if match:
            # This link points to a storyline containing several articles on one page.
            article_id = match.groups(1)
            article = self.parse_article_from_storyline(response, article_id)
        else:
            article = self.parse_single_article_page(response)
        return article


    def parse_article_from_storyline(self, response, article_id):
        """
        Parse the article with id article_id from the storyline page.
        """
        referred_article = response.xpath('//li[@id="{0}"]'.format(article_id))

        # search for article title
        title_parts = referred_article.xpath('descendant::div[@id="articlehead"]/h1/text()').extract()
        if len(title_parts) > 0:
            title = ' '.join(set(title_parts)).encode('utf-8').strip()
        else:
            title = ''

        # search for article published date
        datetime_elements_parts = referred_article.xpath('descendant::small[@id="pubdate"]/strong')
        if len(datetime_elements_parts) > 0:
            datetime_iso_str = self.parse_published_datetime(datetime_elements_parts)
        else:
            datetime_iso_str = ''

        # search for article intro text
        article_intro_parts = referred_article.xpath('descendant::div[@id="articlehead"]/div[@id="intro"]/strong/text()').extract()
        article_intro = ' '.join([x.strip().encode('utf-8') for x in article_intro_parts]).strip()

        # search for article full text
        article_full_text_fragments = referred_article.xpath('descendant::div[@id="articlebody"]/descendant::p/text()').extract()
        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['datetime'] = datetime_iso_str
        article['text'] = article_full_text
        return article



    def parse_single_article_page(self, response):
        """
        Parse the article from a page containing a single article
        """

        # search for article title
        title_parts = response.xpath('//div[@id="articlehead"]/h1')
        if len(title_parts) > 0:
            title_parts_str = [x.encode('utf-8') for x in title_parts[0].xpath('text()').extract()]
            title = ' '.join(title_parts_str).strip()
        else:
            title = ''

        # search for article published date
        datetime_element_parts = response.xpath('//small[@id="pubdate"]/strong')
        if len(datetime_elements_parts) > 0:
            datetime_iso_str = self.parse_published_datetime(datetime_element_parts)
        else:
            datetime_iso_str = ''

        # search for article intro text
        article_intro_parts = response.xpath('//div[@id="article"]/div[@id="articlehead"]/div[@id="intro"]/strong/text()').extract()
        article_intro = ' '.join([x.strip().encode('utf-8') for x in article_intro_parts])

        # search for article full text
        article_full_text_fragments = response.xpath('//div[@id="article"]/div[@id="articlebody"]/div[contains(concat(" ", normalize-space(@class), " "), " articlecontent ")]/descendant::*/text()').extract()
        article_full_text = '\n'.join([x.strip().encode('utf-8') for x in article_full_text_fragments]).strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['datetime'] = datetime_iso_str
        article['text'] = article_full_text
        return article