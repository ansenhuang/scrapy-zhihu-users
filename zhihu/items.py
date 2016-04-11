# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    name = scrapy.Field()
    bio = scrapy.Field()
    location = scrapy.Field()
    business = scrapy.Field()
    gender = scrapy.Field()
    avatar = scrapy.Field()
    education = scrapy.Field()
    major = scrapy.Field()
    employment = scrapy.Field()
    position = scrapy.Field()
    content = scrapy.Field()
    ask = scrapy.Field()
    answer = scrapy.Field()
    agree = scrapy.Field()
    thanks = scrapy.Field()
