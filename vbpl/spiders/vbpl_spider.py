# -*- coding: utf-8 -*-

import scrapy
from scrapy.spiders import CrawlSpider , Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
#from bs4 import BeautifulSoup, Comment
from scrapy.conf import settings
#from selenium import webdriver
import time
import datetime
from ..items import VbplItem
from ..items import RelatedDocumentItem
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import re
from pymongo import MongoClient
class TrangVangVietNamSpider(CrawlSpider):
	name = "vbpl"
	allowed_domains = [
		"http://vbpl.vn/",
		"vbpl.vn"
	]

	start_urls = [	
		'http://vbpl.vn/Pages/portal.aspx'
	]

	__queue = [
		
	]


	# #To continue crawling without dumplicate documents
	# client = MongoClient(settings.get('MONGODB_URI'))
	# db = client[settings.get('MONGODB_DATABASE')]

	# cursor = db[settings.get("CRAWLER_COLLECTION")].find({}, {"url": 1})
	# for i in cursor:
	# 	if 'url' in i:
	# 		__queue.append('^' + i['url'] + '$')


	#To continue crawling without dumplicate documents
	client = MongoClient(settings.get('MONGODB_URI'))
	db = client[settings.get('MONGODB_DATABASE')]

	cursor = db[settings.get("CRAWLER_COLLECTION")].find({}, {"document_id": 1})
	for i in cursor:
		if 'document_id' in i:
			__queue.append('^http:\/\/vbpl.vn\/\w+\/Pages\/vbpq-toanvan.aspx\?ItemID=' + i['document_id'] + '$')


	# Rules for extracting links
	rules = [
	    Rule(
	    	LinkExtractor(allow=(
	    		r'^http:\/\/vbpl.vn\/\w+\/Pages\/vbpq-toanvan.aspx\?ItemID=\d{5}$'
	    	), deny=__queue,
	    	restrict_xpaths=[
	    	]),
	    	callback='parse_fulltext_data', follow=True
	    	),

	    Rule(
	    	LinkExtractor(allow=(
	    		'http:\/\/vbpl.vn\/\w+\/Pages\/vanban.aspx\?(cqbh|idLoaiVanBan|fromyear=).*'
	    	), deny=__queue),
	    	follow=True
	    	),

	    # Extract area (eg. TW, Bac Ninh, TP Ho Chi)
		Rule(
			LinkExtractor(
				allow=(),
				deny=__queue,
				restrict_xpaths=[
					"//div[@class='box-toplink']"
				]),
			follow=True
			),
	    ]

	def extract(self,sel,xpath,split = ' '):
		try:
			data = sel.xpath(xpath).extract()
			text = filter(lambda element: element.strip(),map(lambda element: element.strip(), data))
			return split.join(text)
			# return re.sub(r"\s+", "", ''.join(text).strip(), flags=re.UNICODE)
		except Exception, e:
			raise Exception("Invalid XPath: %s" % e)


	def parse_related_document(self, response):
		# Get back vbpl item from response metadata
		vbpl_item = response.meta['vbpl_item']
		
		rows_labels = response.xpath("//div[@class='content']/table/tbody/tr")

		# related document list
		related_document_list = list()

		for row_label in rows_labels:
			# Extract relating tpye
			relating_type = self.extract(row_label, "td[@class='label']//text()", '')

			rows_docs = row_label.xpath("td/ul[@class='listVB']/li/div[@class='item']/p[@class='title']/a")

			for row_doc in rows_docs:
				
				related_document_item = RelatedDocumentItem()

				# Get related document id
				related_doc_url = self.extract(row_doc, "@href", '')
				related_document_item['related_document_id'] =  re.search("\d+", related_doc_url).group()

				# Get relateing type
				related_document_item['relating_type'] = relating_type

				# Adding related doc item to list
				related_document_list.append(related_document_item)


		# Add to vbpl item
		vbpl_item['related_documents'] = related_document_list

		return vbpl_item

	def parse_attribute_data(self, response):
		SO_KI_HIEU = 'S\xe1\xbb\x91 k\xc3\xbd hi\xe1\xbb\x87u'
		NGAY_BAN_HANH = 'Ng\xc3\xa0y ban h\xc3\xa0nh'
		LOAI_VAN_BAN = 'Lo\xe1\xba\xa1i v\xc4\x83n b\xe1\xba\xa3n'
		NGAY_CO_HIEU_LUC = 'Ng\xc3\xa0y c\xc3\xb3 hi\xe1\xbb\x87u l\xe1\xbb\xb1c'
		NGUON_THU_THAP = 'Ngu\xe1\xbb\x93n thu th\xe1\xba\xadp'
		NGAY_DANG_CONG_BAO = 'Ng\xc3\xa0y \xc4\x91\xc4\x83ng c\xc3\xb4ng b\xc3\xa1o'
		NGANH = 'Ng\xc3\xa0nh'
		LINH_VUC = 'L\xc4\xa9nh v\xe1\xbb\xb1c'
		CO_QUAN_BAN_HANH = 'C\xc6\xa1 quan ban h\xc3\xa0nh/ Ch\xe1\xbb\xa9c danh / Ng\xc6\xb0\xe1\xbb\x9di k\xc3\xbd'
		PHAM_VI = 'Ph\xe1\xba\xa1m vi'

		# Get back vbpl item from response metadata
		vbpl_item = response.meta['vbpl_item']

		# Get effect status
		vbpl_item['effect'] = self.extract(response, "//div[@class='vbInfo']/ul/li[1]/text()", '')

		# Get title
		vbpl_item['title'] = self.extract(response, "//div[@class='vbProperties']/table/tbody/tr[1]/td[@class='title']//text()", '')

		rows = response.xpath("//div[@class='vbProperties']/table/tbody/tr/td")

		for row in rows:
			label = self.extract(row,"text()", '').encode('UTF-8')
			if label == SO_KI_HIEU: vbpl_item['official_number'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == NGAY_BAN_HANH: vbpl_item['issued_date'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == LOAI_VAN_BAN: vbpl_item['legislation_type'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == NGAY_CO_HIEU_LUC: vbpl_item['effective_date'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == NGUON_THU_THAP: vbpl_item['source'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == NGAY_DANG_CONG_BAO: vbpl_item['gazette_date'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == NGANH: vbpl_item['department'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == LINH_VUC: vbpl_item['field'] = self.extract(row, "following-sibling::td[1]//text()")
			elif label == CO_QUAN_BAN_HANH:
				vbpl_item['issuing_office'] = self.extract(row, "following-sibling::td[1]//text()")
				vbpl_item['signer_title'] = self.extract(row, "following-sibling::td[2]//text()")
				vbpl_item['signer_name'] = self.extract(row, "following-sibling::td[3]//text()")
			elif label == PHAM_VI: vbpl_item['effective_area'] = self.extract(row, "following-sibling::td[1]//text()")

		# parse related documents
		yield scrapy.Request(response.url.replace('thuoctinh', 'vanbanlienquan'),
			meta = {'vbpl_item': vbpl_item},
			callback=self.parse_related_document)

	def parse_fulltext_data(self, response):
		se = re.search('\d+', response.url)

		if se is not None:
			# Init vbpl item
			vbpl_item = VbplItem()

			# Get url
			vbpl_item['url'] = response.url

			# Get crawl date
			vbpl_item['crawl_date'] = datetime.datetime.strftime(datetime.datetime.now(),"%b %d %Y %H:%M:%S")

			# Get document id
			vbpl_item['document_id'] = se.group()

			# Get document content
			vbpl_item['content'] = self.extract(response, "//div[@id='toanvancontent']//text()")

			# Return to attributes site of law document
			return scrapy.Request(response.url.replace('toanvan', 'thuoctinh'),
			meta = {'vbpl_item': vbpl_item},
			callback=self.parse_attribute_data)
