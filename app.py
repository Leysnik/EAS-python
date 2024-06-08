'''Main flask run file'''
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
    '''
    Class that describe sqlite table operation
    '''
    index = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    oSum = db.Column(db.Float)
    category = db.Column(db.Integer)
    cashback = db.Column(db.Float)
    mcc = db.Column(db.Integer)
    description = db.Column(db.String(100))

class Categories(db.Model):
    '''
    Class that describe sqlite table categories
    '''
    index = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), primary_key=True)

MAIN_ROUTE = "index.html"
ONE_PERIOD_ROUTE = "stat_page_one_period.html"
GROUP_PERIOD_ROUTE = "stat_page_group.html"
CATEGORY_ROUTE = "stat_category.html"
EMPTY_DF_ROUTE = "error.html"

@app.route('/')
def index():
    '''
    Route display main interface to load excel file or build plots by params
    '''
    data = {"start_date" : "None",
             "end_date" : "None"}
    if db.session.query(Operation).first():
        data["start_date"] = str(db.session.query(Operation).first().date)
        data["end_date"] = str(db.session.query(Operation).order_by(Operation.index.desc())
                               .first().date)
        categories = map(lambda x: x[0], db.session.query(Categories.category).all())
        data["categories"] = categories
    return render_template(MAIN_ROUTE, data=data)

@app.route('/load_data', methods=['POST'])
def load_data():
    '''
    Endpoint to load file
    '''
    if request.method == 'POST':
        file = request.files['file']
        data_manipulator.load_data(file, db)
    return redirect('/', Response=None)

@app.route('/drop', methods=['GET'])
def drop_db():
    '''
    Endpoint to clear datebase if required
    '''
    db.session.commit()
    db.drop_all()
    db.create_all()
    return redirect('/', Response=None)

@app.route('/build_one_period', methods=['GET'])
def one_period():
    '''
    Route show stats and plot for selected period with params:
        strange_operations: outliers in the data
        transactions: are required to show transfers in the plot
    '''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    transactions = int(request.args.get('remittance'))
    strange_operations = request.args.get('HLoperations') == '0'
    data = data_manipulator.build_one_period(db, start_date, end_date,
                                             strange_operations, transactions)
    if data == -1:
        return render_template(EMPTY_DF_ROUTE)
    return render_template(ONE_PERIOD_ROUTE, data=data)

@app.route('/build_list_period', methods=['GET'])
def group_period():
    '''
    Route show stats and plots for selected period with params:
        strange_operations: outliers in the data
        transactions: are required to show transfers in the plot
        period: numder of days in the one subperiod
    '''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if end_date < start_date:
        return render_template(EMPTY_DF_ROUTE)
    transactions = int(request.args.get('remittance'))
    strange_operations = request.args.get('HLoperations') == '0'
    period = int(request.args.get('period'))
    data = data_manipulator.build_group_period(db, start_date, end_date,
                                               strange_operations, transactions, period)
    if data == -1:
        return render_template(EMPTY_DF_ROUTE)
    return render_template(GROUP_PERIOD_ROUTE, data_list=data)

@app.route('/build_categories', methods=['GET'])
def category_period():
    '''
    Route show stats and plots for selected period with params:
        strange_operations: outliers in the data
        transactions: are required to show transfers in the plot
        category: selected category to show magazines transactions
    '''
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    if end_date < start_date:
        return render_template(EMPTY_DF_ROUTE)
    strange_operations = request.args.get('HLoperations') == '0'
    category = request.args.get('category')
    data = data_manipulator.build_category(db, start_date, end_date,
                                           strange_operations, category=category)
    if data == -1:
        return render_template(EMPTY_DF_ROUTE)
    return render_template(CATEGORY_ROUTE, data=data)

if __name__ == '__main__':
    app.run(HOST, PORT, debug=True)
