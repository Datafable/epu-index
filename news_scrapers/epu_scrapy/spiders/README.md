# News spiders

This directory contains spiders to scrape news websites.

## General behaviour

Every spider will first read the settings from the [crawling settings file](../crawling_settings.json) and determine the
start url to start the scraping from. In general (with the exception of the *Standaard* and *De Tijd* spiders, that have
to log on first) the start page will be the journals search page where it will perform a search for articles related to
the term given in the settings file. The search is limited by the period given in the settings file.

All links pointing to resulting articles will be followed and the article pages will be scraped. All spiders are able to
browse to subsequent pages if the search results are too long. The following article's attributes will be parsed:

* Title
* Url
* Author
* Datetime (the timestamp on which the article was published)
* Intro (this is a small introduction paragraph, often accompanying the article)
* Text

TODO: insert link to W3C Xpath doc
The name of the journal will be appended to the output too. The outputs returned by Scrapy are called *items* and the
`Article` item is defined in the [items source file](../items.py). Scrapy (and hence, the spiders implemented here)
relies heavily on XPath to target elements of interest. XPath is a standard syntax for finding elements in a html
document tree based on their attribute values (such as id or class) or their hierarchical position in the tree. It is
well documented at the [W3C website](link to W3C) and many examples are given on Stack Overflow.

Due to differing structures of the different news websites, the news scrapers implementations can differ. The four most
straight forward implementations are the ones for *De Morgen*, *Gazet van Antwerpen*, *Het Belang van Limburg* and *Het
Nieuwsblad*. The spiders for *De Redactie* and *Het Laatste Nieuws* needed to circumvent more complex site structures
and/or client-side JavaScript code that loads content dynamically. *De Standaard* and *De Tijd* require authentication
before we can scrape the websites contents.

TODO: explain how the output gets in the database

## De Morgen

* spider: [`demorgen_spider.py`](./demorgen_spider.py)
* spider name: demorgen

The website of *De Morgen* does not allow to search for articles published the day before the spider is running. It uses a
`from` and `to` parameter in the search, but when both these dates are set to the date for yesterday, no results are
returned (the `to` parameter is exclusive and hence prevents any article to match the query). Therefore, in contrast to
the other spiders, the spider will include the articles of the current day. This means that some articles will be
scraped two times, but these duplicates are prevented from entering the database.

The *De Morgen* spider uses [Scrapy Rules](**insert link**) to crawl the search results. The first rule will follow TODO: insert link to scrapy Rules)
links to subsequent search pages recursively. The second rule will follow links to article pages. Note the
`restrict_xpath` parameter that limits the links to the ones in the `ul` element with class `articles-list`. This
prevents the spider from following links to articles that are shown in the websites header or sidebar.

The second rule has a `callback` argument pointing to the `parse_article` function of the spider. If a link matches this
rule (i.e. if a link to an article is found in the articles-list element), the response of the call to that link will
be parsed with the `parse_article` method. This method will parse all required attributes from the page and returns an
`Article` item.

## De Redactie

* spider: [`deredactie_spider.py`](./deredactie_spider.py)
* spider name: deredactie

This spider is one of the most complex spiders in this directory with several functions needed to scrape the search
results. The behaviour of this spider is not based on rules, because the complex structure of this site prevented

## Standaard

* spider: [`destandaard_spider.py`](./destandaard_spider.py)
* spider name: standaard

TODO: Document De Standaard spider

## De Tijd

TODO: Document De Tijd spider

## Gazet van Antwerpen

* spider: [`gva_spider.py`](gva_spider.py)
* spider name: gva

The `gva_spider` first determines the period of interest by reading the `period` property in the
[settings file](../crawling_settings.json). Based on this period and the term given in the settings file, a start url
will be constructed. This url links to a search page where the spider searches for articles related to the given term
and limited to the dates defined with the `period` property. This is done in the `set_start_urls` function.

Every link in the response of the start url is matched against the rules that are defined in the spider. The first rule
will match links to subsequent results pages while the second rule will match links to actual articles.

The article pages are processed using the `parse_article` function. This function will parse all required article
attributes from the page and return an `Article` item.

## Het Belang van Limburg

* spider: [`hbvl_spider.py`](hbvl_spider.py)
* spider name: hbvl

The `hbvl` spider's implementation is very similar to the `gva_spider`. A `set_start_urls` will construct the search url
using the `term` and `period` properties defined in the [settings file](../crawling_settings.json). Two rules are
defined in the spider that check every link in every returned response. The first rule matches links to subsequent
search results pages while the second rule matches links to article pages. Article pages are processed using the
`parse_article` function and this function returns an `Article` item.

## Het Laatste Nieuws

* spider: [`hln_spider.py`](hln_spider.py)
* spider name: hln

Similar to the other spiders, the `hln_spider` will first determine the start url using the `set_start_urls` function.
Two rules are defined in the spider that check every link in every returned response. The first rule matches links to
subsequent search results pages while the second rule matches links to article pages. Article pages are processed using
the `parse_article` function and this function returns an `Article` item.

TODO: Check if you deleted those parse and parse_list methods

## Het Nieuwsblad

* spider: [`nieuwsblad_spider.py`](nieuwsblad_spider.py)
* spider name: nieuwsblad

The `nieuwsblad` spider's implementation is again very similar to the `gva_spider`. A `set_start_urls` will construct
the search url using the `term` and `period` properties defined in the [settings file](../crawling_settings.json). Two
rules are defined in the spider that check every link in every returned response. The first rule matches links to
subsequent search results pages while the second rule matches links to article pages. Article pages are processed using
the `parse_article` function and this function returns an `Article` item.