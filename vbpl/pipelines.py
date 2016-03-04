# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy import log
from middleware.sqlite4lsmmiddlewares import LSMEngine
class VbplPipeline(object):
    def __init__(self):
        connection = MongoClient(settings.get('MONGODB_URI'))
        db = connection[settings['MONGODB_DATABASE']]
        # db.authenticate(settings['MONGODB_USERNAME'], settings['MONGODB_PASSWORD'])
        self.collection = db[settings['CRAWLER_COLLECTION']]

    def process_item(self, item, spider):
    	data = dict(item)
    	if data['document_id'] not in LSMEngine.db:
    		LSMEngine.db['document_id'] = '1'
    		self.collection.insert(data)
        return item
