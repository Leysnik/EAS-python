import pandas as pd
import numpy as np
import matplotlib as plt
import seaborn as sns

import config

def getDFfromDB(db) -> pd.DataFrame:
    '''
    get db(sql) data to pandas DataFrame
    '''
    return pd.read_sql_table("operation", db.engine.connect())


def loadData(file, db):
    '''
    Load xlsx file to db(sql)
    '''
    df = pd.read_excel(file)
    df = prepareDF(df)
    df.to_sql("operation", con=db.engine, if_exists='replace')

def prepareDF(df: pd.DataFrame) -> pd.DataFrame:
    '''
    This function prepare DataFrame for entry the db:
        Rename columns to valid names
        Drop failed operations
        Drop unnecessary columns 
    '''
    df.rename(columns=config.COLUMN_NAMES, inplace=True)
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, format="%d.%m.%Y").dt.date
    df = df.drop(df[df["status"] == "FAILED"].index)

    df = df.drop(config.USELESS_COLUMNS, axis = 1)
    
    return df

def selectRecords(df: pd.DataFrame, transfer: int, strange_transactions: bool) -> pd.DataFrame:
    '''
    Select rows by parameters:
        transfer:
            1 - keep incoming transfers
            2 - keep outgoing transfers
            0 - drop all tranfers
        strange_tranactions:
            drop 5% most expensive and cheapes operations
    '''
    if transfer == 2:
        df = df.drop(df[(df["category"] == "Переводы") & (df["oSum"] > 0)].index, axis=0)
    elif transfer == 1:
        df = df.drop(df[(df["category"] == "Переводы") & (df["oSum"] < 0)].index, axis=0)
    elif transfer == 0:
        df = df.drop(df[df["category"] == "Переводы"].index, axis=0)

    return df

def last_month(df: pd.DataFrame) -> pd.DataFrame:
    '''
    This function creates DataFrame for the last month 
    '''
    last_date = df["date"].iloc[0]
    lastOffset = last_date - pd.DateOffset(days=last_date.day)
    mask = (df["date"] > lastOffset.date()) & (df["date"] <= last_date)
    return df[mask]

def make_df_list(df: pd.DataFrame, days: int = 0) -> pd.DataFrame:
    '''
    This function creates list of DataFrames grouped by date interval
    '''
    first_date = df["date"].iloc[0]
    last_date = df["date"].iloc[-1]
    df_list = []
    if days == 0:
        df_list.append(last_month(df))
        first_date -= pd.DateOffset(days=first_date.day)
        offset = pd.DateOffset(months=1)
    else:
        first_date = pd.Timestamp(first_date)
        offset = pd.DateOffset(days=days)

    iter = first_date - offset
    while iter.date() >= last_date:
        mask = (df["date"] > iter.date()) & (df["date"] <= first_date.date())
        df_list.append(df[mask])
        first_date -= offset
        iter -= offset
    return df_list

    

# def testfunc(db: pd.DateFrame, transfer: int):
#     df = selectRecords(getDFfromDB(db), transfer, False)
# #    df = df[df["category"] == "Переводы"]
#     df = last_month(df)
#     return df.to_json()
