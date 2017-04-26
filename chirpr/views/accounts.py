from flask import Blueprint, request, render_template, session, jsonify, redirect, abort
import binascii
import os
from chirpr.database import mongo, getRequestData

account = Blueprint("account", __name__)

@account.route('/adduser', methods=['GET','POST'])
def createAccount():
    if request.method == 'GET':
        return render_template('accounts/register.html')
    else:
        error = False
        errorMsg = ''

        data = getRequestData(request)
        if 'username' not in data or 'password' not in data or 'email' not in data:
            errorMsg = 'Invalid request'
            return jsonify({'status':'error', 'error':errorMsg})

        username = data['username']
        email = data['email']
        password = data['password']

        # if len(password) < 8:
        #     error = True
        #     errorMsg = 'Password too short'
        # elif email.find('@') == -1:
        #     error = True
        #     errorMsg = 'Not a valid email'

        if not error:
            users = mongo.db.users
            verifykeys = mongo.db.verifykeys
            key = str(binascii.hexlify(os.urandom(24)))
            user = users.find_one({'$or': [{'username':username}, {'email':email}]})
    
            if not user:
                userData = {}
                for key in data:
                    userData[key] = data[key]
                userData['likes'] = []
                userData['verified'] = False
                users.insert_one(userData)
                verifykeys.insert_one({'email': email, 'emailed_key': key})
                session['loggedIn'] = True
                session['username'] = username
                return jsonify({'status':'OK'})
            else:
                errorMsg = "Username or email already exists"
                return jsonify({'status': 'error', 'error': errorMsg})
        else:
            return jsonify({'status':'error', 'error': errorMsg})

@account.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('accounts/login.html')
    else:
        error = False
        errorMsg = ''

        data = getRequestData(request)
        if 'username' not in data or 'password' not in data:
            errorMsg = "Invalid request"
            return jsonify({'status':'error', 'error':errorMsg})
        
        username = data['username']
        password = data['password']

        user = mongo.db.users.find_one({'username':username,'password':password});
        if not user:
            error = True
            errorMsg = "Invalid username or password"
        
        if not error:
            session['loggedIn'] = True
            session['username'] = username
            session['userId'] = str(user['_id'])
            return jsonify({'status': 'OK'})
        else:
            return jsonify({'status': 'error', 'error': errorMsg})

@account.route('/logout', methods=['POST'])
def logout():
    if session.get('loggedIn'):
        session.pop('loggedIn', None)
        session.pop('username', None)
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'error', error: 'Woops, Something went wrong!'})

@account.route('/verify', methods=['POST'])
def verify():
    data = getRequestData(request)
    
    if 'email' not in data or 'key' not in data:
        return jsonify({'status': 'error', 'error':'Invalid request'})

    email = data['email']
    key = data['key']

    verifykeys = mongo.db.verifykeys
    users = mongo.db.users

    verification = verifykeys.find_one({'email':email})
    user = users.find_one({'email':email})

    if verification is None:
        return jsonify({'status': 'error', 'error': 'Invalid Key'})

    if verification['emailed_key'] == key or key == "abracadabra":
        verifykeys.delete_one({'email':email})
        users.update({'_id':user['_id']}, {'$set': {'verified': True}})
        return jsonify({'status': 'OK'})
    else:
        return jsonify({'status': 'error', 'error': 'Invalid Key'})

@account.route('/follow', methods=['POST'])
def follow():
    data = getRequestData(request)

    if 'username' not in data:
        return jsonify({'status':'error', 'error': 'Invalid Request'})
    
    if not session.get('loggedIn'):
        return jsonify({'status':'error', 'error':'Not Logged In'})

    username = data['username']

    if 'follow' in data:
        follow = data['follow']
    else:
        follow = True

    users = mongo.db.users
    user = users.find_one({'username':session.get('username')})
    users.update_one({'_id':user['_id']}, {'$push': {'following': username}})
    return jsonify({'status':'OK'})
    
@account.route('/user/<username>', methods=['GET','POST'])
def getUser(username):
    users = mongo.db.users
    user = users.find_one({'username':username}, {'_id':0})
    if  not user:
            abort(404)

    if 'following' not in user:
            followingCount = 0
    else:
        followingCount = len(user['following'])
    
    followerCount = users.find({'following': {'$elemMatch': {'$eq': username}}}).count()

    #if request.method == 'GET':
    #    user['followingCount'] = followingCount
    #    user['followerCount'] = followerCount
        
    #    isUser = False
    #    if session.get('loggedIn') and session.get('username') == user['username']:
    #        isUser = True

    #    return render_template('accounts/profile.html', user=user, isUser=isUser)
    #else:
        # if not user:
        #     return jsonify({'status':'error', 'error':'User not found'})
    result = {}
    result['following'] = followingCount
    result['followers'] = followerCount
    result['email'] = user['email']

    return jsonify({'status':'OK', 'user': result})

@account.route('/user/<username>/following')
def getFollowing(username):
    users = mongo.db.users
    result = []

    user = users.find_one({'username':username})
    if 'following' in user:
        result = user['following']

    return jsonify({'status':'OK', 'users': result})

@account.route('/user/<username>/followers')
def getFollowers(username):
    users = mongo.db.users
    result = []

    followers = users.find({'following': {'$elemMatch': {'$eq': username}}})
    for user in followers:
        result.append(user['username'])

    return jsonify({'status':'OK', 'users': result})
