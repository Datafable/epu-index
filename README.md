# EPU index

At the [Applied Data Mining research group](http://www.applieddatamining.com/) at the University of Antwerp, a
classifier was developed to classify news articles as Economic Policy Uncertainty (EPU) related or not. The EPU index is
the number of EPU related articles per day divided by the number of news journals that were crawled. In order to get a
daily update of the EPU index, a number of scrapers were developed that can scrape Belgian (Flemish) news jounals every
day. The resulting EPU index data is available to the broad public [here](#link-does-not-work-yet).

The application consists of 3 parts: the web scrapers, a web application and a front end.

* [Scrapers](./news_scrapers): 8 scrapers were developed using Python's Scrapy framework. Scrapy is well documented
[here](http://doc.scrapy.org/en/0.24/) and a [tutorial](http://doc.scrapy.org/en/0.24/intro/tutorial.html) will guide
you through Scrapy's main concepts. The crawlers that do the actual crawling work are called *spiders* and the spiders
that were developed are documented [here](./news_scrapers/epu_scrapy/spiders).
* [Web application](./webapp): The web application is the place where all articles and their EPU classification scores
are stored. The web application is developed using [Django](https://www.djangoproject.com/) and the most important part
are the [models](./webapp/epu_index/models.py). The data in the web application is served using [Django's REST
framework](http://www.django-rest-framework.org/) to the front end.
* [Front end](./frontend): The front end contains purely html and JavaScript and uses the [C3](http://c3js.org/) and
[d3-cloud](https://github.com/jasondavies/d3-cloud) libraries. The data that is needed for generating the charts are
fetched from the web applications REST end points.

# Installation

Check out the [installation documentation](installation.md).

# Configuration

The application allows for some configurable parameters. Most notably:

* **Journal authentication settings**: these should be set in the [crawling settings
file](news_scrapers/epu_scrapy/crawling_settings.example.json). See the [crawlers documentation](news_scrapers/epu_scrapy)
for more information about those settings.
* **Period and term to scrape**: these can also be found in the [crawling settings
file](news_scrapers/epu_scrapy/crawling_settings.example.json).
* **Model file**: this file should contain a comma separated list of words and their weights to be used to score an
article. It should include a header `word,weight`. This setting in the [crawling settings
file](news_scrapers/epu_scrapy/crawling_settings.example.json) points to the model file. Since this models file is used
by the scraper, only newly scraped articles will be affected when a new file is used.
* **EPU Score Cutoff**: this cutoff defines at which score articles are considered positive. You can alter this cutoff
in the [models file](webapp/epu_index/models.py#L7) but note that you will have to re-run the custom django command
[`calculate_daily_epu`](webapp/epu_index/management/commands) for all dates already in the database.
* **Stopwords**: the stopwords are documented as a tuple in the [models file](webapp/epu_index/models.py#L5). To generate
such a tuple from a text file, you can use the stand alone script [stopwords_to_tuple.py](stopwords_to_tuple.py) and
paste the result in the models file.