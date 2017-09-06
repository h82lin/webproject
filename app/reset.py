from pymongo import MongoClient

client = MongoClient()
db = client.solverstatistics
collection = db.stats_collection

collection.remove({})                    #removes all documents from mongo database collection
