import datetime
import os

import pandas as pd


def create_performence_csv(total_nodes, success_node, performence):
    todaydate = datetime.date.today()
    current_month = todaydate.strftime("%Y-%m")
    filename = "perfomence_{}.csv".format(current_month)

    date = [todaydate]
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
    filename = "perfomence_{}.csv".format(current_month)
    data = pd.read_csv(filename)
    print(data)
    

# create_performence_csv(200, 180, 89.4)
read_performence_csv()

# import glob
# import datetime
# import pandas as pd
# import re
# def InputFile_Exists_For_Stat():
#     try:
#         outfile_path = "/home/ubuntu/perl-to-python/nigeria/TEMP"
#         Input_file = glob.glob(outfile_path+"/MTN_nigeria_backup_tracker_2020-12-01.xlsx")
#         todaydate = datetime.date.today()
#         if todaydate.day < 15:
#             firstday = todaydate.replace(day=1)
#             lastday = firstday - datetime.timedelta(1)
#             currnt_month_files = outfile_path + "/MTN_nigeria_backup_tracker_" + lastday.strftime("%Y-%m") + "*.xlsx"
#             Input_file_past = glob.glob(currnt_month_files)
#             Input_file.extend(Input_file_past)
#         return Input_file
#     except IndexError:
#         return "None"


# def find_date(fileName):
#     m = re.search("([0-9]{4}\-[0-9]{2}\-[0-9]{2})", fileName)
#     date_YMD = m.group(0)
#     date_object = datetime.datetime.strptime(date_YMD, '%Y-%m-%d')
#     return date_object.strftime("%d-%b")


# Input_file = InputFile_Exists_For_Stat()
# if Input_file == "None":
#     sys.exit("Error message")



# df_SDP = pd.DataFrame()
# df_SDP_GEO_RED = pd.DataFrame()
# df_NGVS_GEO_RED = pd.DataFrame()
# df_AIR = pd.DataFrame()
# df_CCN = pd.DataFrame()
# df_NGVS = pd.DataFrame()
# df_OCC = pd.DataFrame()

# for file in Input_file:
#     print(file)
#     inputsheet_to_df_map = pd.read_excel(file, sheet_name=None, skiprows=6)
#     # print(inputsheet_to_df_map['SDP'])
#     # For SDP
#     df = inputsheet_to_df_map['SDP_Daily']
#     df.insert(0, 'Date', find_date(file))
#     df.insert(0, 'Node', 'SDP')
#     # df_SDP = df_SDP.append(df)

#     # # For SDP_GEO_RED
#     # df = inputsheet_to_df_map['SDP-GEO-RED']
#     # df.insert(0, 'Date', find_date(file))
#     # df.insert(0, 'Node', 'SDP-GEO-RED')
#     # df_SDP_GEO_RED = df_SDP_GEO_RED.append(df)

#     # # For NGVS_GEO_RED
#     # df = inputsheet_to_df_map['NGVS-GEO-RED']
#     # df.insert(0, 'Date', find_date(file))
#     # df.insert(0, 'Node', 'NGVS-GEO-RED')
#     # df_NGVS_GEO_RED = df_NGVS_GEO_RED.append(df)

#     # # For AIR
#     # df = inputsheet_to_df_map['AIR']
#     # df.insert(0, 'Date', find_date(file))
#     # df.insert(0, 'Node', 'AIR')
#     # df_AIR = df_AIR.append(df)

#     # # For CCN
#     # df = inputsheet_to_df_map['CCN']
#     # df.insert(0, 'Date', find_date(file))
#     # df.insert(0, 'Node', 'SDP')
#     # df_CCN = df_CCN.append(df)

#     # # For NGVS
#     # df = inputsheet_to_df_map['NGVS']
#     # df.insert(0, 'Date', find_date(file))
#     # df.insert(0, 'Node', 'NGVS')
#     # df_NGVS = df_NGVS.append(df)

#     # # OCC
#     # df = inputsheet_to_df_map['OCC']
#     # df.insert(0, 'Date', find_date(file))
#     # df.insert(0, 'Node', 'OCC')
#     # df_OCC = df_OCC.append(df)

# print(df_SDP)
# # print(df_SDP_GEO_RED)
# # print(df_NGVS_GEO_RED)
# # print(df_AIR)
# # print(df_CCN)
# # print(df_NGVS)