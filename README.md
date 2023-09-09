# NewsAPI Website

## Script for automatically scraping newest news articles

### Workflow:

1. Get N newest articles (urls and headlines) (`news_handler.py`)

2a. Scrape given urls to get full article texts (`article_parser.py`)

2b. Format and filter raw article texts (`article_parser.py`)

3a. Rewrite articles and headlines (`ai_writer.py`)

3b. Get article main topic (`ai_writer.py`)

3c. Get a photo from Google Storage that correspondents to the article main topic (`ai_writer.py` + `gcp_handler.py`)

4a. Return rewritten article text, rewritten headline and an image from Google Storage (...)

4b. Reformat rewritten article text, inserting html code for advertisment (...)

4c. Post article + headline + image (...)

### Blob naming

#### images:

`gs://images/donald_trump/donald_trump_1.jpg`
`gs://images/donald_trump/donald_trump_2.jpg`
`gs://images/joe_biden/joe_biden_1.jpg`
