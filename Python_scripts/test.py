import pymongo

conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)
db = client.mars
collection = db.mars


data = list(db.collection.find())
print(type(data))
print(data[len(data) - 1])
# print(data['featured_img']) 