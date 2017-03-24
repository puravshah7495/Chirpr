from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime

db = SQLAlchemy()

def getRequestData(request):
    if request.get_json():
        return request.get_json()
    else:
        return request.values

class Users(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	password = db.Column(db.String(255), nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	verified = db.Column(db.Boolean(), nullable=False, default=False)

	def __init__(self, username, password, email):
		self.username = username
		self.password = password
		self.email = email

class Chirps(db.Model):
	__tablename__ = 'chirps'
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(140), nullable=False)
	user_id = db.Column(db.Integer.ForeignKey('users.id'), nullable=False)
	timestamp = db.Column(db.DateTime, server_default=db.func.now())

class VerifyKeys(db.Model):
	__tablename__ = 'verifykeys'
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
	emailed_key = db.Column(db.String(100))

	user = db.relationship('Users', backref='verifykey')

	def __init__(self, user_id, emailed_key):
		self.user_id = user_id
		self.emailed_key = emailed_key

def create_app():
	app = Flask(__name__)
	app.config.from_pyfile('app.cfg')
	db.init_app(app)
	return app