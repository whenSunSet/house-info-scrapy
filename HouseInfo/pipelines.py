# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymongo 


class HouseinfoPipeline:
    house_info_collection_name = 'house_info_simple'
    zufang_info_collection_name = 'zufang_info_simple'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri="mongodb://192.168.31.185:27017",
            mongo_db="dev"
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if (item["isZuFang"]):
            zuFangCol = self.db[self.zufang_info_collection_name]
            zuFangExist = (zuFangCol.count_documents({"roomId": item["roomId"]}) > 0) 
            if (not zuFangExist):
                self.db[self.zufang_info_collection_name].insert_one(ItemAdapter(item).asdict())
        else:
            houseInfoCol = self.db[self.house_info_collection_name]
            houseInfoExist = (houseInfoCol.count_documents({"roomId": item["roomId"]}) > 0) 
            if (not houseInfoExist):
                self.db[self.house_info_collection_name].insert_one(ItemAdapter(item).asdict())
        return item 
