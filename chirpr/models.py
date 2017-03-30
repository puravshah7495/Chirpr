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
	#id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), primary_key=True)
	password = db.Column(db.String(255), nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	verified = db.Column(db.Boolean(), nullable=False, default=False)

	#verifykey = db.relationship('VerifyKeys', backref='user', uselist=False)


	def __init__(self, username, password, email):
		self.username = username
		self.password = password
		self.email = email

class Chirps(db.Model):
	__tablename__ = 'chirps'
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(140), nullable=False)
	username = db.Column(db.String(20), db.ForeignKey('users.username'), nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.utcnow())

	def __init__(self, content, username):
		self.content = content
		self.username = username


	def toDict(self):
                return { 
                        'id': self.id,
                        'content': self.content,
                        'username': self.username,
                        'timestamp': self.timestamp
                }


class VerifyKeys(db.Model):
	__tablename__ = 'verifykeys'
	email = db.Column(db.String(255), primary_key=True)
	emailed_key = db.Column(db.String(100))

	def __init__(self, email, emailed_key):
		self.email = email
		self.emailed_key = emailed_key

def create_app():
	app = Flask(__name__)
	app.config.from_pyfile('app.cfg')
	db.init_app(app)
	return app
