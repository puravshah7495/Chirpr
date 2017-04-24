from flask import Blueprint, request, render_template, jsonify, send_file
from chirpr.database import getRequestData, mongo
import base64
import os

media = Blueprint("mediaMod", __name__)

@media.route('/addMedia', methods=['GET','POST'])
def addMedia():
    if request.method == "GET":
        return render_template('media.html')
    error = False
    errorMsg = ''
    files = mongo.db.media

    mediaFile = request.files['content']
    data = base64.b64encode(mediaFile.read())
    f_id = files.insert_one({'content': data})

    return jsonify({'status': 'OK', 'id': f_id})

@media.route('/media/<ObjectId:id>', methods=['GET'])
def getMedia(id):
    files = mongo.db.media
    error = False
    errorMsg = ''

    f = files.find_one({'_id': id})
    print id, f
    tmp = open('tmp.png', "w")
    tmp.write(f['content'].decode('base64'))
    tmp.close()
    return send_file('tmp.png', mimetype='image/png')


