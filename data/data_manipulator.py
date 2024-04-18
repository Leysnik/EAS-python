import pandas as pd
import numpy as np
import matplotlib as mpl
from flask_sqlalchemy import SQLAlchemy

def getDFfromDB(operation):
    ...

def loadData(file, db):
    df = pd.read_excel(file)
    df = prepareDF(df)
    df.to_sql("operation", con=db.engine, if_exists='append')

def prepareDF(df):
    df = df.drop(df[df["Статус"] == "FAILED"].index)

    df = df.drop(['Дата операции', 'Номер карты', 'Статус',
           'Сумма платежа', 'Валюта платежа', 'Валюта операции',
           'Бонусы (включая кэшбэк)', 
           'Округление на инвесткопилку',
           'Сумма операции с округлением'], axis = 1)
    
    dictCol = {"index" : "index",
               "Дата платежа" : "date",
               "Сумма операции" : "oSum",
               "Категория" : "category",
               "Кэшбэк" : "cashback",
               "MCC" : "mcc",
               "Описание" : "description"
               }
    print(df.head())
    df.rename(columns=dictCol, inplace=True)
    #if not isTransferNeeded:
    #    df = df.drop(df[df["Категория"] == "Переводы"].index)
    return df