from chirpr import app
from flask_pymongo import PyMongo

def getRequestData(request):
    if request.get_json():
        return request.get_json()
    else:
        return request.values

mongo = PyMongo(app)