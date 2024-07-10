# EAS-python
Application for analyzing expenses on banking transactions.

## Introduction
This application builds charts and reports on banking transactions based on uploading data from your personal account(my case : tinkoff). /
```config.py``` has a few settings to set the names of columns in your xls file and configure DBG server.

## Input data
Excel file with this structure
![xls structure](/repo_img/xlsStructure.png)
This are necessary columns. If your file contains more columns, you must specify them in the file ```config.py```
## SETUP
1. import this repo
2. ```pip install -r requirements.txt```
3. make migrations to create SQLite DB:
```
python
from app import app, db
app.app_context().push()
db.create_all()
exit()
```
4. ```flask run``` to start app.
