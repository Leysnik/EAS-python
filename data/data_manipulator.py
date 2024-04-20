import pandas as pd
import numpy as np
import matplotlib as plt
from flask_sqlalchemy import SQLAlchemy
import seaborn as sns
import config

def getDFfromDB(operation):
    ...

def loadData(file, db):
    df = pd.read_excel(file)
    df = prepareDF(df)
    df.to_sql("operation", con=db.engine, if_exists='replace')

def prepareDF(df):
    df.rename(columns=config.COLUMN_NAMES, inplace=True)

    df = df.drop(df[df["status"] == "FAILED"].index)

    df = df.drop(config.USELESS_COLUMNS, axis = 1)
    #if not isTransferNeeded:
    #    df = df.drop(df[df["Категория"] == "Переводы"].index)
    return df