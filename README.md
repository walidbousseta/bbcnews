
# Scraping the BBCNews data
A scrapy webscraper that can scrape articles from bbc news website
```
make sure that all packages in requirements.txt are installed
```

## Running the spiders
To create a scrapy project:
```
scrapy startproject bbcnews
```

Start scrapping
```
scrapy crawl bbcnews
```

## The structure of bbcNews return
I scrape for each news article the following data:
```
    title = the article title
    url = url into tthe article content
    summary = the summary showing in the first page
    tags = tags show in the first page 
    header = in the article page we extract the header 
    body = the article body news
    related = related topics to the article
    datetime = when the article published
```

## to start the DB_API
```
    $-> python main.py
```

<img src=DB_API/images/app.png>
