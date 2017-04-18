from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.database import mongo, getRequestData
from datetime import datetime
from bson.objectid import ObjectId
import pymongo
import traceback

chirpMod = Blueprint("chirpMod", __name__)

@chirpMod.route('/additem', methods=['POST'])
def addItem():
	error = False
	errorMsg = ''
	
	if not session.get('loggedIn'):
		error = True
		errorMsg = 'Not logged in'
		return jsonify({'status': 'error', 'error': errorMsg})

	data = getRequestData(request)
	query = {}

	if 'content' not in data:
		error = True
		errorMsg = 'Invalid request'
		return jsonify({'status': 'error', 'error': errorMsg})

	if 'parent' in data:
		query['parent'] = data['parent']

	if 'media' in data:
		query['parent'] = data['media']

	content = data['content']
	if (len(content) > 140):
		return jsonify({'status':'error', 'error':'Chirp is too long'})

	query['content'] = content
	query['username'] = session.get('username')
	query['timestamp'] = datetime.utcnow()

	chirps = mongo.db.chirps
	chirp = chirps.insert_one(query)
	return jsonify({'status':'OK', 'id':str(chirp.inserted_id)})

@chirpMod.route('/item/<id>', methods=['GET'])
def getChirp(id):
	error = False
	errorMsg = ''
	if id is None:
		return jsonify({'status':'error', 'error':'Invalid request'})

	chirps = mongo.db.chirps
	chirp = chirps.find_one({'_id': ObjectId(id)})
	if chirp is None:
		return jsonify({'status':'error', 'error':'ID not found'})
	chirp['_id'] = str(chirp['_id'])
	return jsonify({'status':'OK', 'item':chirp})

@chirpMod.route('/item/<id>', methods=['DELETE'])
def deleteChirp(id):
	error = False
	errorMsg = ''
	if id is None:
		return jsonify({'status':'error', 'error':'Invalid request'})
	chirp = mongo.db.chirps.delete_one({'_id':ObjectId(id)})
	# ADD CODE TO DELETE ALL THE ASSOCIATED MEDIA FROM CEPH OR WHATEVER
	return jsonify({'status':'OK'})

@chirpMod.route('/search', methods=['POST'])
def search():
	error = False
	errorMsg = ''

	chirps = mongo.db.chirps
	data = getRequestData(request)
	print data
	query = { '$and' : [] }
	
	if not 'timestamp' in data:
		timestamp = datetime.utcnow()
	else:
		timestamp = datetime.utcfromtimestamp(float(data['timestamp']))

	query["$and"].append({"timestamp" : {'$lte' : timestamp}})

	if 'limit' in data:
		limit = data['limit']
	else:
		limit = 25

	if 'q' in data:
		searchquery = data['q']
		query["$and"].append({"$text" : {"$search" : searchquery}})

	if 'username' in data:
		username = data['username']
		query["$and"].append({"username" : {"$eq" : username}})

	if session.get('loggedIn') is True:
		if 'following' in data:
			if data['following'] is True or data['following'] is None:
				user = mongo.db.users.find_one({"username" : {"$eq" : session.get('username')}})
				if 'following' not in user:
					user['following'] = []
				query["$and"].append({"following" : {"$in" : user['following']}})
			
	query = chirps.find(query).sort([('timestamp',-1)]).limit(limit) 
	chirpList = []
	for chirp in query:
		chirp['id'] = str(chirp['_id'])
		chirp.pop('_id', None)
		chirpList.append(chirp)
	return jsonify({'status':'OK', 'items':chirpList})
	# except Exception as e:
	# 	print traceback.print_exc()
	# 	return jsonify({'status':'error', 'error':errorMsg})
