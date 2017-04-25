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
    chirps = mongo.db.chirps
    query = {}

    if 'content' not in data:
        error = True
        errorMsg = 'Invalid request'
        return jsonify({'status': 'error', 'error': errorMsg})

    if 'media' in data:
        query['media'] = data['media']

    content = data['content']
    if (len(content) > 140):
        return jsonify({'status': 'error', 'error': 'Chirp is too long'})

    query['content'] = content
    query['user_id'] = ObjectId(session.get('userId'))
    query['timestamp'] = datetime.utcnow()
    query['retweets'] = 0
    query['replies'] = []
    query['likes'] = []

    if 'parent' in data:
        parent = data['parent']
        query['parent'] = parent
    else:
        parent = -1

    chirp = chirps.insert_one(query)

    if content[:3].capitalize() == "RT ":
        chirps.find({"content": content})
        chirps.update_many({"content": content}, {"$inc": {
            "retweets": 1,
        }})

    if parent >= 0:
        chirp['_id'] = str(chirp['_id'])
        chirps.update_one({'_id': parent}, {'$push': {'replies': chirp}})

    return jsonify({'status': 'OK', 'id': str(chirp.inserted_id)})


@chirpMod.route('/item/<ObjectId:id>', methods=['GET'])
def getChirp(id):
    error = False
    errorMsg = ''
    if id is None:
        print("invalid request")
        return jsonify({'status': 'error', 'error': 'Invalid request'})

    chirps = mongo.db.chirps
    chirp = chirps.find_one({'_id': id})
    if chirp is None:
        print("couldn't find id")
        return jsonify({'status': 'error', 'error': 'ID not found'})
    chirp['_id'] = str(chirp['_id'])
    print("found")
    return jsonify({'status': 'OK', 'item': chirp})


@chirpMod.route('/item/<ObjectId:id>', methods=['DELETE'])
def deleteChirp(id):
    error = False
    errorMsg = ''
    if id is None:
        return jsonify({'status': 'error', 'error': 'Invalid request'})

    chirp = mongo.db.chirps.find_one({'_id': id})
    mongo.db.media.delete_one({'_id': ObjectId(chirp['media'])})
    mongo.db.chirps.delete_one({'_id': id})

    return jsonify({'status': 'OK'})


@chirpMod.route('/item/<id>/like', methods=['POST'])
def like(id):
    error = False
    errorMsg = ''
    if not session.get('loggedIn'):
        error = True
        errorMsg = 'Not logged in'
        return jsonify({'status': 'error', 'error': errorMsg})

    data = getRequestData(request)
    if 'like' not in data:
        return jsonify({'status': 'error'})

    chirps = mongo.db.chirps
    users = mongo.db.users

    userId = ObjectId(session.get('userId'))
    like = data['like']

    # update in both users and chirps
    if like is True:
        chirps.update_one({'_id': ObjectId(id)}, {"$push": {"likes": str(userId)}})
        users.update_one({'_id': ObjectId(userId)}, {'$push': {'likes': id}})
    else:
        chirps.update_one({'_id': ObjectId(id)}, {"pull": {"likes": str(userId)}})
        users.update_one({'_id': ObjectId(userId)}, {'pull': {'likes': id}})
    return jsonify({'status': 'OK'})


@chirpMod.route('/search', methods=['POST'])
def search():
    chirps = mongo.db.chirps
    users = mongo.db.users
    data = getRequestData(request)

    query = {'$and': []}

    if not 'timestamp' in data:
        timestamp = datetime.utcnow()
    else:
        timestamp = datetime.utcfromtimestamp(float(data['timestamp']))

    query["$and"].append({"timestamp": {'$lte': timestamp}})

    if 'limit' in data:
        limit = data['limit']
    else:
        limit = 25

    # filter on search query
    if 'q' in data:
        searchquery = data['q']
        query["$and"].append({"$text": {"$search": searchquery}})

    if 'username' in data:
        username = data['username']
        user = users.find_one({'username': username})
        query["$and"].append({"user_id": {"$eq": user['_id']}})

    # get chirps made in reply to requested tweet
    if 'parent' in data:
        parent = data['parent']
        query["$and"].append({"parent": {"$eq": parent}})

    # get chirps made by users you are following
    if session.get('loggedIn') is True:
        if 'following' in data:
            if data['following'] is True or data['following'] is None:
                user = mongo.db.users.find_one({"username": {"$eq": session.get('username')}})
                if 'following' not in user:
                    user['following'] = []
                query["$and"].append({"following": {"$in": user['following']}})

    # sort by interest or time
    if 'rank' in data:
        rank = data['rank']
    else:
        rank = 'interest'

    if rank == 'time':
        # query.append({"$sort": {
        #     "timestamp": -1
        # }})
        query['sort'] = {
            "timestamp": -1
        }
    else:
        query['sort'] = {
            {"$sum": ["retweets", {"$size": "likes"}]}: -1
        }
        # query.append(
        #     {
        #         "$sort": {
        #             {"$sum":
        #                  ["retweets", {"$size": "likes"}]
        #              }: -1
        #         }
        #     }
        # )

    # get replies for all filtered tweets
    if 'replies' in data:
        replies = data['replies']
    else:
        replies = True

    # results = chirps.aggregate(query).limit(limit)
    # results = chirps.aggregate([
    #     {'$match': query},
    #     {'$group': {"_id":"_id", 'rank':{"$sum": ["retweets", {"$size": "likes"}]}}},
    #     {'$project': {'content':1, 'replies':1, 'user_id':1, 'timestamp':1, 'likes':1, 'retweets':1}},
    #     {'$limit':limit}
    # ])
    results = chirps.find(query).limit(limit);

    print results

    chirpList = []
    for chirp in results:
        chirp['id'] = str(chirp['_id'])
        chirp.pop('_id', None)
        chirpList.append(chirp)
    return jsonify({'status': 'OK', 'items': chirpList})
