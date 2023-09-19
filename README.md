# NewsAPI Website

## Module 1.

This module takes N records of newest articles via API from NewsAPI. For now, it is focused only on CNN data. Originally, it would returns a dictionary of such structure:

```bash
{
"status": "ok",
"totalResults": 37,
"articles": [
{
"source": {
"id": null,
"name": "Yahoo Entertainment"
},
"author": "HYUNG-JIN KIM",
"title": "North Korea says Kim Jong Un is back home from Russia, where he deepened 'comradely' ties with Putin - Yahoo News",
"description": "North Korea said Tuesday that leader Kim Jong Un has returned home from a trip to Russia where he deepened “comradely fellowship and friendly ties” with...",
"url": "https://news.yahoo.com/north-korea-says-kim-jong-043321527.html",
"urlToImage": "https://s.yimg.com/ny/api/res/1.2/.ARbrn5F8cPQzDk6nNYtVw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyMDA7aD03OTg-/https://media.zenfs.com/en/ap.org/7952b858d1fb02ec03b7fa7525ebd52b",
"publishedAt": "2023-09-19T10:23:06Z",
"content": "SEOUL, South Korea (AP) North Korea said Tuesday that leader Kim Jong Un has returned home from a trip to Russia where he deepened comradely fellowship and friendly ties with President Vladimir Putin… [+2628 chars]"
},
{
"source": {
"id": "financial-times",
"name": "Financial Times"
},
"author": null,
"title": "Live news: YouTube demonetises Russell Brand's channel following sexual misconduct allegations - Financial Times",
"description": "News, analysis and comment from the Financial Times, the worldʼs leading global business publication",
"url": "https://www.ft.com/content/6f17a6a5-100d-49c8-8899-606343055265",
"urlToImage": null,
"publishedAt": "2023-09-19T10:21:46Z",
"content": "What is included in my trial?\r\nDuring your trial you will have complete digital access to FT.com with everything in both of our Standard Digital and Premium Digital packages.\r\nStandard Digital includ… [+1494 chars]"
}
...
]}
```

Thanks to a wrapper `customize_output` if returns a list of tuples like this:

```bash
[
    (url, title (=headline), content (=first N words of an article)),
    (url, title (=headline), content (=first N words of an article)),
    ...
]

```

## Module 2.

This module is responsible for rewriting articles and headline, topic and named entities detection, putting these information all together and passing it to the posting bot.

## Module 3.

Posting post add articles to rge Django DB. To populate DB with fake data, run:

```
python mysite\manage.py import_articles
```

Beforehand you can manipulate with body of funtion `handle` in `mysite\newsapp\management\commands\import_articles.py` to set custom variables.

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
