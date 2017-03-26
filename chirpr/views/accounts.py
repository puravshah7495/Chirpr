from flask import Blueprint, request, render_template, session, jsonify, redirect
from chirpr.models import db, Users, getRequestData
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
            newUser = Users(username, password, email)
            db.session.add(newUser)
	    db.session.flush()
            db.session.commit()
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
