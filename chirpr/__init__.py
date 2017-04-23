from flask import Flask, render_template

app = Flask(__name__)
app.config.from_pyfile('app.cfg')

from views.accounts import account
from views.chirps import chirpMod
from views.media import media
from flask_pymongo import PyMongo
from database import mongo

app.register_blueprint(account)
app.register_blueprint(chirpMod)
app.register_blueprint(media)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
