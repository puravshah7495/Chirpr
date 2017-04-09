from chirpr import app
from flask_pymongo import PyMongo
import pymongo

def getRequestData(request):
    if request.get_json():
        return request.get_json()
    else:
        return request.values

mongo = PyMongo(app)

with app.app_context():
    chirps = mongo.db.chirps
    chirps.create_index([('content', pymongo.TEXT)])