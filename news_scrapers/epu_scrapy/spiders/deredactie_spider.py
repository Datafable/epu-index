import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from epu_scrapy.items import Article

class RedactieSpider(CrawlSpider):
    name = 'deredactie' # name of the spider, to be used when running from command line
    allowed_domains = ['www.deredactie.be']
    start_urls = ['']
    rules = (
        Rule(LinkExtractor(allow=('zoeken\/.*page=[0-9]+'))),
        Rule(LinkExtractor(allow=('\/cnt\/')), callback='parse_article'),
    ) # if a link matches the pattern in 'allow', it will be followed. If 'callback' is given, that function will be executed with the page that the link points to.

    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('//article/div[2]/div/div/header/h1/text()').extract()
        if len(title_parts) > 0:
            title = title_parts[0].encode('utf-8')
        else:
            title = ''

        # search for article published date
        datetime_str_parts = response.xpath('//article/div[2]/div/div/footer/p/time/@datetime').extract()
        if len(datetime_str_parts) > 0:
            datetime_str = datetime_str_parts[0].encode('utf-8')
        else:
            datetime_str = ''

        # search for div containing all article content
        article_div = response.xpath('//article/div[2]/div/div/div[1]/div[@class="article__body"]')

        # search for article intro text
        article_intro_parts = article_div.xpath('div[@class="article__intro"]/descendant-or-self::text()').extract()
        article_intro = ' '.join([x.strip().encode('utf-8') for x in article_intro_parts])

        # search for article full text
        article_full_text_fragments = article_div.xpath('div[@class="article__intro"]/following-sibling::*/text()').extract()
        article_full_text = '\n'.join([x.strip().encode('utf-8') for x in article_full_text_fragments]).strip()

        # now create an Article item, and return it. All Articles created during scraping will can be written to an output file when the -o option is given.
        article = Article()
        article['intro'] = article_intro
        article['title'] = title
        article['datetime'] = datetime_str
        article['text'] = article_full_text
        return article