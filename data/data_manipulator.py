import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import config

def getDFfromDB(db) -> pd.DataFrame:
    '''
    get db(sql) data to pandas DataFrame
    '''
    return pd.read_sql_table("operation", db.engine.connect())


def loadData(file, db) -> None:
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
            0 - drop all transfers
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

def choose_period(df: pd.DataFrame, first_date: str, last_date: str) -> pd.DataFrame:
    '''
    This function creates DataFrame for the choosen period
    '''
    first_date = pd.to_datetime(first_date, format="%Y-%m-%d").date()
    last_date = pd.to_datetime(last_date, format="%Y-%m-%d").date()
    mask = (df['date'] >= last_date) & (df['date'] <= first_date)
    return df[mask]

def make_df_list(df: pd.DataFrame, days: int = 0) -> list[pd.DataFrame]:
    '''
    This function creates list of DataFrames grouped by day interval
        if days == 0 function groups rows by months 
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
    iterator = first_date - offset
    while iterator.date() >= last_date:
        mask = (df["date"] > iterator.date()) & (df["date"] <= first_date.date())
        df_list.append(df[mask])
        first_date -= offset
        iterator -= offset
    return df_list

def transactions_hist(df: pd.DataFrame):
    '''
    This function build the hist plot: category - sum of transactions in df
    '''
    categories = list(set(df["category"]))
    oSum = []
    for category in categories:
        oSum.append(df[df["category"] == category]["oSum"].abs().sum()) 
    data = pd.DataFrame({"category" : categories,
                              "sum" : oSum})
    plt.figure()
    sns.barplot(data, x="sum", y="category")
    plt.savefig("templates/plots/transactions_gist.png", bbox_inches="tight")

def sum_list(df_list: list[pd.DataFrame]):
    oSum = []
    periods = []
    for i in range(len(df_list)):
        oSum.append(df_list[i]["oSum"].abs().sum())
        periods.append(df_list[i]["date"].iloc[-1])
    return periods, oSum

def periods_hist(df_list: list[pd.DataFrame]):
    '''
    This function build hist plot: start date of df - sum of df
    '''
    periods, oSum = sum_list(df_list)
    data = pd.DataFrame({ "date" : periods,
                           "sum" : oSum})
    plt.figure()
    sns.barplot(data, x="sum", y="date")
    plt.savefig("templates/plots/periods_hist.png", bbox_inches="tight")



def testfunc(db: pd.DateFrame, transfer: int):
    df = selectRecords(getDFfromDB(db), transfer, False)
#    df = df[df["category"] == "Переводы"]
    df = last_month(df)
    return df.to_json()
