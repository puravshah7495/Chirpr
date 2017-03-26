from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.models import db, Users, Chirps, getRequestData
from datetime import datetime
import traceback

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

		chirps = Chirps.query.filter(Chirps.timestamp <= timestamp).order_by(Chirps.timestamp.desc()).limit(limit).all()
		chirpsList = [x.toDict() for x in chirps]
		return jsonify({'status':'OK', 'items':chirpsList})
	except Exception as e:
		print traceback.print_exc()
		return jsonify({'status':'error', 'error':errorMsg})
