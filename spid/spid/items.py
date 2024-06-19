# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SpidItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    firstName = scrapy.Field()
    middleName = scrapy.Field()
    lastName = scrapy.Field()
    birthDay = scrapy.Field()
    birthMonth = scrapy.Field()
    birthYear = scrapy.Field()
    phone = scrapy.Field()
    age = scrapy.Field()
    street = scrapy.Field()
    city = scrapy.Field()
    aprt = scrapy.Field()
    hometown = scrapy.Field()
    
    pass
