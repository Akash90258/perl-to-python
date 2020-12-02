import datetime
import os

import pandas as pd


def create_performence_csv(total_nodes, success_node, performence):
    todaydate = datetime.date.today()
    current_month = todaydate.strftime("%Y-%m")
    filename = "performence/perfomence_{}.csv".format(current_month)

    date = [todaydate.strftime("%d-%b")]

    performence = [performence]
    total_nodes = [total_nodes]
    success_node = [success_node]

    dict = {
        'Date': date,
        'Total_nodes': total_nodes,
        'Success_node': success_node,
        'Percentage': performence
    }
    df = pd.DataFrame(dict)

    # if file does not exist write header 
    if not os.path.isfile(filename):
        df.to_csv(filename, mode='a', encoding='utf-8', index=False)
    else:
        df.to_csv(filename, mode='a', header=False, index=False)


def read_performence_csv():
    todaydate = datetime.date.today()
    current_month = todaydate.strftime("%Y-%m")
    filename = "performence/perfomence_{}.csv".format(current_month)
    data = pd.read_csv(filename)
    data_list = []
    for i, j in data.iterrows():
        data_list.append([j['Date'], j['Percentage']])
    return data_list


def read_success_fail_csv():
    todaydate = datetime.date.today()
    current_month = todaydate.strftime("%Y-%m")
    filename = "performence/perfomence_{}.csv".format(current_month)
    data = pd.read_csv(filename)
    data_list = []
    for i, j in data.iterrows():
        data_list.append([j['Date'], j['Total_nodes'], j['Total_nodes'] - j['Success_node']])
    return data_list
