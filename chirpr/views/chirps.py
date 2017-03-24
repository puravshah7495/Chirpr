from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.models import db, Users, Chirps, getRequestData

chirpMod = Blueprint("chirpMod", __name__)

@chirpMod.route('/additem', methods=['POST'])
def addItem():
	error = False
	errorMsg = ''
	try:
		if session.get('loggedIn'):
			user_id = session.get('user_id')
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

		chirp = Chirps(content, user_id)
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
		if 'timestamp' not in data:
			error = True
			errorMsg = 'Invalid request'

		timestamp = data['timestamp']
		limit = data['limit']

		if not limit:
			limit = 25
		chirps = Chirps.query.filter_by(timestamp=timestamp).limit(limit)
		return jsonify({'status':'error', 'items':chirps})
	except Exception as e:
		print e
		return jsonify({'status':'error', 'error':errorMsg})
