# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# this is the package I use to connect into MongoDb
import pymongo

# in this class we connect into database to insert the data we scrape
class BbcnewsPipeline:
	def __init__(self):
		# first we connect into monogo server , I left the default parameters for user and passeword
		self.conn = pymongo.MongoClient('localhost', 27017)
		# here we create or we call the database name 
		db = self.conn['BBCNews']
		# the same for the table in this database
		self.collection = db['News']

	# in this function we can control the data flow we want to insert into the database
	def process_item(self, item, spider):
		# because of some returns body are empty I add this condition to get only the ones has content
		if item['body']!="":
			# in the item return some other params like download_timeout, depth I don't won't those values in database
			items = {'title':item['title'],
					 'url':item['url'],
					 'summary':item['summary'],
					 'tags':item['tags'],
					 'header':item['header'],
					 'body':item['body'],
					 'related':item['related'],
					 'datetime':item['datetime']}
			self.collection.insert(dict(items))
		return item
