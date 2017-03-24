from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.models import db, Users, Chirps, getRequestData
from datetime import datetime

chirpMod = Blueprint("chirpMod", __name__)

@chirpMod.route('/additem', methods=['POST'])
def addItem():
	error = False
	errorMsg = ''
	try:
		if session.get('loggedIn'):
			username = session.get('username')
		else:
			error = True
			errorMsg = 'Not logged in'

		data = getRequestData(request)

		if ('content' not in data):
			error = True
			errorMsg = 'Invalid request'

		content = data['content']

		if (len('content') > 140):
			return jsonify({'status':'error', 'error':'Chirp is too long'})

		chirp = Chirps(content, username)
		db.session.add(chirp)
		db.session.commit()
		return jsonify({'status':'OK', 'id':chirp.id})
	except Exception as e:
		print e
		return jsonify({'status':'error', 'error':errorMsg})

@chirpMod.route('/item/<int:id>', methods=['GET'])
def getChirp(id):
	error = False
	errorMsg = ''
	try:
		if id is None:
			return jsonify({'status':'error', 'error':'Invalid request'})

		chirp = Chirps.query.filter_by(id=id).first()

		if not chirp:
			return jsonify({'status':'error', 'error':'ID not found'})
		return jsonify({'status':'OK', 'item':chirp.toDict()})
	except Exception as e:
		print e
		return jsonify({'status':'error', 'error':errorMsg})

@chirpMod.route('/search', methods=['POST'])
def search():
	error = False
	errorMsg = ''
	try:
		data = getRequestData(request)
		
		if not 'timestamp' in data:
			timestamp = datetime.utcnow()
			print timestamp
		else:
			timestamp = datetime.utcfromtimestamp(data['timestamp'])
			print timestamp

		if 'limit' in data:
			limit = data['limit']
		else:
			limit = 25

		chirps = Chirps.query.filter(Chirps.timestamp <= timestamp).order_by(Chirps.timestamp.desc()).limit(limit).all()
		print chirps
		chirpsList = [x.toDict() for x in chirps]
		print chirpsList
		return jsonify({'status':'OK', 'items':chirpsList})
	except Exception as e:
		print e
		return jsonify({'status':'error', 'error':errorMsg})
