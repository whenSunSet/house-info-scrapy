# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HouseinfoItem(scrapy.Item):
    # define the fields for your item here like:
    roomId = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    totalPrice = scrapy.Field()
    area = scrapy.Field()
    realArea = scrapy.Field()
    roomLayout = scrapy.Field()
    roomFloor = scrapy.Field()
    roomOrientation = scrapy.Field()
    buildYear = scrapy.Field()
    city = scrapy.Field()
    district = scrapy.Field()
    subDistrict = scrapy.Field()
    community = scrapy.Field()
    online = scrapy.Field()
    hasElevator = scrapy.Field()
    lastBusinessTime = scrapy.Field()
    currentBusinessTime = scrapy.Field()
    businessOwner = scrapy.Field()
    ownerShip = scrapy.Field()
    houseUsage = scrapy.Field()
    mortgageInfo = scrapy.Field()
    houseSellTime = scrapy.Field()
    isZuFang = scrapy.Field()
    pass
