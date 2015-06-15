# News scrapers

This directory contains scrapers in the [spiders](./spiders) directory. The scrapers can be run command line with the `scrapy crawl <spidername>` command. The scrapers use the [crawling_settings.json](./crawling_settings.json) file to look for certain settings:

* `term`: The search term used to query the journals index page.
* `period`:  The date range to which retrieved articles should be limited to. This should be in the form `{"start": date1, "end": date2}` where dates should be in `yyyy-mm-dd` format. Additionally, you can set this to `yesterday`. This will cause the scraper to determine the current date and search for articles published on the day before that.