import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import config

def getDFfromDB(db) -> pd.DataFrame:
    '''
    get db(sql) data to pandas DataFrame
    '''
    df = pd.read_sql_table("operation", db.engine.connect())
    df['date'] = pd.to_datetime(df['date']).dt.date
    return df


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
    df.drop(df[df["status"] == "FAILED"].index, inplace=True)
    df.drop(config.USELESS_COLUMNS, axis = 1, inplace=True)
    return df

def selectRecords(df: pd.DataFrame, transfer: int, strange_transactions: bool=True) -> pd.DataFrame:
    '''
    Select rows by parameters:
        transfer:
            2 - keep outgoing transfers
            0 - drop all transfers
        strange_tranactions:
            drop 5% most expensive and cheapest operations
    '''
    data = dict()
    data["trans_plus"] = df[(df["category"] == "Переводы") & (df["oSum"] > 0)].loc[:, "oSum"].sum()
    data["income"] = df[df["category"] == "Пополнения"].loc[:, "oSum"].sum()
    df.drop(df[(df["category"] == "Переводы") & (df["oSum"] > 0)].index, axis=0, inplace=True)
    if transfer == 0:
        df.drop(df[df["category"] == "Переводы"].index, axis=0, inplace=True)

    if strange_transactions:
        df = df[(df["oSum"] < df["oSum"].quantile(.95)) & (df["oSum"] > df["oSum"].quantile(.05))]
    df.drop(df[df["category"] == "Пополнения"].index, axis=0, inplace=True)
    df.drop(df[df["category"] == "Бонусы"].index, axis=0, inplace=True)
    df["oSum"] = df["oSum"].abs()
    return df, data

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

def transactions_hist(df: pd.DataFrame, index: int):
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
    plt.savefig("static/plots/transactions_hist" + str(index) + ".png", bbox_inches="tight")

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
    plt.savefig("static/plots/periods_hist.png", bbox_inches="tight")

def info_with_stat_period(df: pd.DataFrame, strange_operations: int, transfers: int, plot: int) -> dict:
    bonus = df[df["category"] == "Бонусы"].loc[: , "oSum"].sum()
    df, data = selectRecords(df, transfers, strange_operations)
    data["bonus"] = bonus
    if len(df.index) == 1:
        return -1
    data["sum"] = df["oSum"].sum()
    data["mean"] = round(df["oSum"].mean(), 2)
    data["median"] = round(df["oSum"].median(), 2)
    data["end_period"] = df["date"].iloc[0]
    data["start_period"] = df["date"].iloc[-1]
    transactions_hist(df, plot)
    return data

def build_one_period(db, start_date: str, end_date: str, strange_operations: int, transfers: int) -> dict:
    df = getDFfromDB(db)
    df = choose_period(df, end_date, start_date)
    return info_with_stat_period(df, strange_operations, transfers, 0)

def build_group_period(db, start_date: str, end_date: str, strange_operations: int, transfers: int, period: int) -> dict:
    df = getDFfromDB(db)
    df = choose_period(df, end_date, start_date)
    df_list = make_df_list(df, period)
    data_list = []
    data_list.append(dict())
    data_list[0] = info_with_stat_period(df, strange_operations, transfers, 0)
    periods_hist(df_list)
    plot = 1
    for i in range(len(df_list)):
        data = info_with_stat_period(df_list[i], strange_operations, transfers, plot)
        if data == -1:
            continue
        data["plot"] = plot
        plot += 1
        data_list.append(data)
    return data_list

