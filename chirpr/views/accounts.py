from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.models import db, Users, VerifyKeys,getRequestData
import binascii
import os
# from chirpr import getRequestData

account = Blueprint("account", __name__)

@account.route('/adduser', methods=['GET','POST'])
def createAccount():
    if request.method == 'GET':
        return render_template('accounts/register.html')
    else:
        error = False
        errorMsg = ''

        data = getRequestData(request)
	print data
        if 'username' not in data or 'password' not in data or 'email' not in data:
            error = True
            errorMsg = 'Invalid request'

        username = data['username']
        email = data['email']
        password = data['password']

        if len(password) < 8:
            error = True
            errorMsg = 'Password too short'
	elif email.find('@') == -1:
            error = True
            errorMsg = 'Not a valid email'

        if not error:
            key = str(binascii.hexlify(os.urandom(24)))
            newUser = Users(username, password, email)
            newKey = VerifyKeys(email, key)
            db.session.add(newUser)
            db.session.add(newKey)
            db.session.commit()
	        # db.session.execute("INSERT INTO users (username, password, email, verified) VALUES (:username, :password, :email, :verified)",
			# 	{'username':username, 'password':password, 'email':email,'verified':False})		
            # db.session.execute("INSERT INTO verifykeys (email, emailed_key) VALUES (:email, :key)", {'email':email, 'key':key})
            # db.session.commit()
            session['loggedIn'] = True
            session['username'] = username
            return jsonify({'status':'OK'})
        else:
            return jsonify({'status':'ERROR', 'error': errorMsg})

@account.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('accounts/login.html')
    else:
        error = False
        errorMsg = ''

        data = getRequestData(request)
        if 'username' not in data or 'password' not in data:
            error = True
            errorMsg = "Invalid request"
        
        username = data['username']
        password = data['password']
	print username
	print password
	user = db.session.execute("select * from users where username = :val" , {'val':username}).fetchone()
	#print result
        #user = Users.query.filter(Users.username == username).first()
        print user
	
	if user is None:
            error = True
            errorMsg = "Invalid username or password"
	elif not user.password == password:
	    error = True
	    errorMsg = "Invalid username or password"
        
	if not error:
            print username
            session['loggedIn'] = True
            session['username'] = username
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'ERROR', 'error': errorMsg})

@account.route('/logout', methods=['POST'])
def logout():
    if session.get('loggedIn'):
        session.pop('loggedIn', None)
        session.pop('username', None)
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'ERROR', error: 'Woops, Something went wrong!'})

@account.route('/verify', methods=['POST'])
def verify():
    data = getRequestData(request)
    
    if 'email' not in data or 'key' not in data:
        return jsonify({'status': 'ERROR', 'error':'Invalid request'})

    email = data['email']
    key = data['key']

    verification = db.session.execute("select * from verifykeys where email = :email" , {'email':email}).fetchone()

    if verification is None:
        return jsonify({'status': 'ERROR', 'error': 'Invalid Key'})

    if verification.emailed_key == key or key == "abracadabra":
        db.session.execute("update users set verified = 1 where email = :email", {'email':email})
        db.session.execute("delete from verifykeys where email = :email", {'email': email})
        db.session.commit()
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'ERROR', 'error': 'Invalid Key'})