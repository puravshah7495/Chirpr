from chirpr import app
from flask_pymongo import PyMongo
import pymongo
import gridfs

def getRequestData(request):
    if request.get_json():
        return request.get_json()
    else:
        return request.values

mongo = PyMongo(app)
global fs

with app.app_context():
    chirps = mongo.db.chirps
    mongo.db.chirps.create_index([('content', pymongo.TEXT), ('username', pymongo.TEXT),('timestamp',pymongo.ASCENDING)])
    fs = gridfs.GridFS(mongo.db, collection="fs")