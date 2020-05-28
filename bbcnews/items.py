# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

# in here we declare the items we need 
class BbcnewsItem(scrapy.Item):
    # define the fields for your item here like:
    # image = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    summary = scrapy.Field()
    tags = scrapy.Field()
    header = scrapy.Field()
    body = scrapy.Field()
    related = scrapy.Field()
    datetime = scrapy.Field()


