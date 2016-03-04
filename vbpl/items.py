# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VbplItem(scrapy.Item):
    document_id = scrapy.Field()
    content = scrapy.Field()
    title = scrapy.Field()
    official_number = scrapy.Field()
    legislation_type = scrapy.Field()
    source = scrapy.Field()
    department = scrapy.Field()
    issuing_office = scrapy.Field()
    effective_area = scrapy.Field()
    issued_date = scrapy.Field()
    effective_date = scrapy.Field()
    effect = scrapy.Field()
    gazette_date = scrapy.Field()
    field = scrapy.Field()
    signer_title = scrapy.Field()
    signer_name = scrapy.Field()
    related_documents = scrapy.Field()
    crawl_date = scrapy.Field()
    url = scrapy.Field()

class RelatedDocumentItem(scrapy.Item):
    relating_type = scrapy.Field()
    related_document_id = scrapy.Field()
