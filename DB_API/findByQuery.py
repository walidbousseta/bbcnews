import pymongo as pm

client = pm.MongoClient('localhost', 27017)
db = client['BBCNews']
col = db['news']

col.drop_indexes()
col.create_index([('body','text')], default_language ="english")

words_to_look4 = "Hong Kong"
query = {'$text':{'$search':words_to_look4, '$caseSensitive': True }}
results = col.find(query)

for r in results:
	print(r)

