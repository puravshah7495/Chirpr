from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.models import getRequestData
from chirpr.database import mongo
from datetime import datetime
import traceback

chirpMod = Blueprint("chirpMod", __name__)

@chirpMod.route('/additem', methods=['POST'])
def addItem():
	error = False
	errorMsg = ''
	try:
		if not session.get('loggedIn'):
			error = True
			errorMsg = 'Not logged in'
			return jsonify({'status': 'error', 'error': errorMsg})

		data = getRequestData(request)

		if 'content' not in data:
			error = True
			errorMsg = 'Invalid request'
			return jsonify({'status': 'error', 'error': errorMsg})

		content = data['content']
		username = session.get('username')

		if (len('content') > 140):
			return jsonify({'status':'error', 'error':'Chirp is too long'})

		chirps = mongo.db.chirps
		chirp = chirps.insert_one({'content': content,'username':username,'timestamp':datetime.utcnow()})
		return jsonify({'status':'OK', 'id':str(chirp.inserted_id)})
	except Exception as e:
		traceback.print_exc()
		print e
		return jsonify({'status':'error', 'error':errorMsg})

@chirpMod.route('/item/<id>', methods=['GET'])
def getChirp(id):
	error = False
	errorMsg = ''
	try:
		if id is None:
			return jsonify({'status':'error', 'error':'Invalid request'})

		chirps = mongo.db.chirps
		chirp = chirps.find_one({'_id': id})
		print chirp
		if chirp is None:
			return jsonify({'status':'error', 'error':'ID not found'})
		return jsonify({'status':'OK', 'item':chirp})
	except Exception as e:
		print e
		return jsonify({'status':'error', 'error':errorMsg})

@chirpMod.route('/search', methods=['POST'])
def search():
	error = False
	errorMsg = ''
	try:
		data = getRequestData(request)
		print data
		if not 'timestamp' in data:
			timestamp = datetime.utcnow()
		else:
			timestamp = datetime.utcfromtimestamp(float(data['timestamp']))
		#timestamp = datetime.strptime(data['timestamp'], "%a, %d %b %Y %H:%M:%S %Z");

		if 'limit' in data:
			limit = data['limit']
		else:
			limit = 25

		# chirps = Chirps.query.filter(Chirps.timestamp <= timestamp).order_by(Chirps.timestamp.desc()).limit(limit).all()
		chirps = mongo.db.chirps
		query = chirps.find({'timestamp': {'$lte': timestamp}}).sort([('timestamp',-1)]).limit(limit) 
		chirpList = []
		for chirp in query:
			chirp['_id'] = str(chirp['_id'])
			chirpList.append(chirp)
		return jsonify({'status':'OK', 'items':chirpList})
	except Exception as e:
		print traceback.print_exc()
		return jsonify({'status':'error', 'error':errorMsg})
