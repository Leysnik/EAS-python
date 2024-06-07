import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import config

def get_df_from_db(db):
    '''
    get db(sql) data to pandas DataFrame
    '''
    df = pd.read_sql_table("operation", db.engine.connect())
    categories = pd.read_sql_table("categories", db.engine.connect())
    df['date'] = pd.to_datetime(df['date']).dt.date
    df["category"] = df["category"].apply(lambda x: categories.loc[x, "category"])
    return df


def load_data(file, db):
    '''
    Load xlsx file to db(sql)
    '''
    df = pd.read_excel(file)
    df = prepare_df(df)
    categories = pd.DataFrame({"category" : list(set(df["category"]))})
    categories.to_sql("categories", con=db.engine, if_exists="replace")
    df["category"] = df["category"].apply(lambda x: categories[categories["category"] == x].index[0])
    df.to_sql("operation", con=db.engine, if_exists='replace')

def prepare_df(df):
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

def select_records(df, transfer,
                  strange_transactions=True, category=None):
    '''
    Select rows by parameters:
        transfer:
            2 - keep outgoing transfers
            0 - drop all transfers
        strange_tranactions:
            drop 5% most expensive and cheapest operations
    '''
    data = {}
    if category:
        df.drop(df[df["category"] != category].index, axis=0, inplace=True)
    else:
        data["trans_plus"] = df[(df["category"] == "Переводы") & (df["oSum"] > 0)].loc[:, "oSum"].sum()
        data["income"] = df[df["category"] == "Пополнения"].loc[:, "oSum"].sum()
        df.drop(df[(df["category"] == "Переводы") & (df["oSum"] > 0)].index, axis=0, inplace=True)
        if transfer == 0:
            df.drop(df[df["category"] == "Переводы"].index, axis=0, inplace=True)
        df.drop(df[df["category"] == "Пополнения"].index, axis=0, inplace=True)
        df.drop(df[df["category"] == "Бонусы"].index, axis=0, inplace=True)

    if strange_transactions:
        df = df[(df["oSum"] < df["oSum"].quantile(.95)) & (df["oSum"] > df["oSum"].quantile(.05))]
    df["oSum"] = df["oSum"].abs()
    return df, data

def last_month(df):
    '''
    This function creates DataFrame for the last month 
    '''
    last_date = df["date"].iloc[0]
    last_offset = last_date - pd.DateOffset(days=last_date.day)
    mask = (df["date"] > last_offset.date()) & (df["date"] <= last_date)
    return df[mask]

def choose_period(df, first_date, last_date):
    '''
    This function creates DataFrame for the choosen period
    '''
    first_date = pd.to_datetime(first_date, format="%Y-%m-%d").date()
    last_date = pd.to_datetime(last_date, format="%Y-%m-%d").date()
    mask = (df['date'] >= last_date) & (df['date'] <= first_date)
    return df[mask]

def make_df_list(df, days=0):
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
        mask = (df["date"] >= iterator.date()) & (df["date"] <= first_date.date())
        if len(df.index) != 0:
            df_list.append(df[mask])
        first_date -= offset
        iterator -= offset
    return df_list

def category_hist(df, search, index):
    '''
    This function build the hist plot: magazin - sum of transactions in df
    '''
    search_list = list(set(df[search]))
    osum = []
    for iterator in search_list:
        osum.append(df[df[search] == iterator]["oSum"].abs().sum())
    data = pd.DataFrame({search: search_list,
                              "sum" : osum})
    plt.figure()
    sns.barplot(data, x="sum", y=search)
    plt.savefig("static/plots/transactions_hist" + str(index) + ".png", bbox_inches="tight")

def mean_hist(df, search, index):
    search_list = list(set(df[search]))
    mean_values = []
    for iterator in search_list:
        mean_values.append(df[df[search] == iterator]["oSum"].abs().mean())
    data = pd.DataFrame({search: search_list,
                              "sum" : mean_values})
    plt.figure()
    sns.barplot(data, x="sum", y=search)
    plt.savefig("static/plots/mean_hist" + str(index) + ".png", bbox_inches="tight")

def sum_list(df_list):
    '''
    Support func to create sum for periods
    '''
    osum = []
    periods = []
    for i in range(len(df_list)):
        if len(df_list[i]) == 0:
            continue
        osum.append(df_list[i]["oSum"].abs().sum())
        periods.append(df_list[i]["date"].iloc[-1])
    return periods, osum

def periods_hist(df_list):
    '''
    This function build hist plot: start date of df - sum of df
    '''
    periods, osum = sum_list(df_list)
    data = pd.DataFrame({ "date" : periods,
                           "sum" : osum})
    plt.figure()
    sns.barplot(data, x="sum", y="date")
    plt.savefig("static/plots/periods_hist.png", bbox_inches="tight")

def info_with_stat_period(df, strange_operations, transfers,
                          plot=0, category=None):
    '''
    Support func to build data dict and plots for routes
    '''
    if len(df.index) == 0:
        return -1
    bonus = df[df["category"] == "Бонусы"].loc[: , "oSum"].sum()
    df, data = select_records(df, transfers, strange_operations, category=category)
    data["bonus"] = bonus
    if len(df.index) == 0:
        return -1
    data["sum"] = round(df["oSum"].sum(), 2)
    data["mean"] = round(df["oSum"].mean(), 2)
    data["median"] = round(df["oSum"].median(), 2)
    data["end_period"] = df["date"].iloc[0]
    data["start_period"] = df["date"].iloc[-1]
    if category:
        category_hist(df, "description", plot)
        mean_hist(df, "description", plot)
    else:
        category_hist(df, "category", plot)
        mean_hist(df, "category", plot)
    return data

def build_one_period(db, start_date, end_date, strange_operations,
                     transfers):
    df = get_df_from_db(db)
    df = choose_period(df, end_date, start_date)
    return info_with_stat_period(df, strange_operations, transfers, 0)

def build_group_period(db, start_date, end_date, strange_operations,
                       transfers, period):
    df = get_df_from_db(db)
    df = choose_period(df, end_date, start_date)
    if len(df.index) == 0:
        return -1
    df_list = make_df_list(df, period)
    data_list = []
    data_list.append({})
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

def build_category(db, start_date, end_date, strange_operations, category):
    df = get_df_from_db(db)
    df = choose_period(df, end_date, start_date)
    data = info_with_stat_period(df, strange_operations, 0, 0, category=category)
    return data
