

import pymongo

class BBCNews(object):
	def __init__(self):
		# first we connect into monogo server , I left the default parameters for user and passeword
		self.client = pymongo.MongoClient('localhost', 27017)
		# here we create or we call the database name 
		self.db = self.client.BBCNews
		# the same for the table in this database
		self.collection = self.db.News

	def print_all(self):
		print('print all docs :')
		for doc in self.collection.find():
			print(doc)


if __name__ == '__main__':
	bbc = BBCNews()
	print('start the API...')
	bbc.print_all()


