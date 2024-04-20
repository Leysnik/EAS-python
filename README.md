# EAS-python
Application for analyzing expenses on banking transactions

## Introduction
This application builds charts and reports on banking transactions based on uploading data from your personal account (tinkoff)

## Input data
Excel file with this structure
<!-- ![img](/repo_img/xslStructure.png) -->
## SETUP
1. import this repo
2. make migrations to create SQLite DB:
```
python
from main import app, db
app.app_context().push()
db.create_all()
exit()
```
