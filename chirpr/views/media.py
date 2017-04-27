from flask import Blueprint, request, render_template, jsonify, send_file
from chirpr.database import getRequestData, mongo
from werkzeug.utils import secure_filename
import base64
import os
import gridfs

media = Blueprint("mediaMod", __name__)

@media.route('/addmedia', methods=['GET','POST'])
def addMedia():
    if request.method == "GET":
        return render_template('media.html')
    error = False
    errorMsg = ''
    # files = mongo.db.media
    fs = gridfs.GridFS(mongo.db)
    mediaFile = request.files['content']
    id = fs.put(mediaFile, filename=mediaFile.filename)
    # data = base64.b64encode(mediaFile.read())
    # f = files.insert_one({'content': data})
    print "successful add media"
    return jsonify({'status': 'OK', 'id': str(id)})

@media.route('/media/<ObjectId:id>', methods=['GET'])
def getMedia(id):
    files = mongo.db.media
    error = False
    errorMsg = ''

    fs = gridfs.GridFS(mongo.db)
    img = fs.get(id)
    print img.filename
    # f = files.find_one({'_id': id})
    # print id, f
    # tmp = open('tmp.png', "w")
    # tmp.write(f['content'].decode('base64'))
    # tmp.close()
    response = mongo.send_file(img.filename)
    response.headers['Content-Type'] = 'image/jpeg'
    print "successful get media"
    return response


