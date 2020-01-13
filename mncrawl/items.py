# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MncrawlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NodeItem(scrapy.Item):
    ip = scrapy.Field()


class ConnectionItem(scrapy.Item):
    ip_from = scrapy.Field()
    ip_to = scrapy.Field()


class NodeStatusItem(scrapy.Item):
    ip = scrapy.Field()
    api = scrapy.Field()
    api_url = scrapy.Field()
    full_node = scrapy.Field()
