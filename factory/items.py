# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class NewsItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # event = Field()
    # currency = Field()

    currencies = Field()
    events = Field()
    impacts = Field()
    actual = Field()
    forecast = Field()
    previous = Field()
    time = Field()