from flask import Flask, render_template
from models import create_app, db
from views.accounts import account
from views.chirps import chirpMod

app = create_app()
app.app_context().push()
db.create_all(app=app)

app.register_blueprint(account)
app.register_blueprint(chirpMod)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
