from flask import Blueprint, request, render_template, jsonify, send_file, abort
from chirpr.database import getRequestData, mongo, fs
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

    mediaFile = request.files['content']
    id = fs.put(mediaFile, filename=mediaFile.filename)

    return jsonify({'status': 'OK', 'id': str(id)})

@media.route('/media/<ObjectId:id>', methods=['GET'])
def getMedia(id):
    files = mongo.db.media
    error = False
    errorMsg = ''

    try:
        img = fs.get(id)
        print img.filename

        response = mongo.send_file(img.filename)
        response.headers['Content-Type'] = 'image/jpeg'
        return response
    except gridfs.errors.NoFile:
        print  id
        abort(404)


