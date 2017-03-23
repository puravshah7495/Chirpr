from flask import Flask, render_template
from models import create_app, db
from views.accounts import account

app = create_app()
app.app_context().push()
db.create_all(app=app)

app.register_blueprint(account)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)