from flask import Flask
from flask import render_template, request, redirect
from config import HOST, PORT
from flask_sqlalchemy import SQLAlchemy
from data import data_manipulator

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Operation(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    oSum = db.Column(db.Float)
    category = db.Column(db.String(100))
    cashback = db.Column(db.Float)
    mcc = db.Column(db.Integer)
    description = db.Column(db.String(100))


MAIN_ROUTE = "index.html"

@app.route('/')
def index():
    dates = {"start_date" : "None",
             "end_date" : "None"}
    if db.session.query(Operation).first():
        dates["start_date"] = str(db.session.query(Operation).first().date)
        dates["end_date"] = str(db.session.query(Operation).order_by(Operation.index.desc()).first().date)
        print(dates)
    return render_template(MAIN_ROUTE, dates=dates)

@app.route('/load_data', methods=['POST'])
def load_data():
    if request.method == 'POST':
        file = request.files['file']
        data_manipulator.loadData(file, db)
        return redirect("/", Response=None)
        
@app.route('/build', methods=['GET'])
def build_info():
    return data_manipulator.testfunc(db, 3)

@app.route('/drop', methods=['GET'])
def drop_db():
    db.session.commit()
    db.drop_all()
    db.create_all()
    return redirect("/", Response=None)


if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)