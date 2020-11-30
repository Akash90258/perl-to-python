
import sys

reload(sys)

sys.setdefaultencoding('utf8')

import logging
from datetime import date
import datetime

import openpyxl
import pandas as pd
from utils import *

print("Process Started")
day = datetime.datetime.today() 
day_DD_MON_YYYY = day.strftime("%d-%b-%Y")
# Initialising Logging module
log_file_path = "./logs/logs_{}.log".format(str(date.today()))
logging.basicConfig(
    level=logging.INFO,
    # filename=log_file_path
)

logging.info("Starting Automation...")

# Loading config.ini file into a dictionary
logging.info("Loading Config.ini")
config_data = load_config_ini()

# initialising variable from config.ini
logging.info("Loading Variables from config.ini ")
Base_path = config_data['base_dir_inp_files']
Template_file = config_data['template_file']
Output_File = config_data['output_file_path'] + \
              config_data['output_file_prefix'] + \
              str(date.today()) + ".xlsx"
pma_nw_file_path = config_data['pma_nw_file_path']

try:

    # reading pma_nw_final.conf and creating dictionary
    logging.info("Loading Configurations from pma_nw_file_path.conf")
    updated_pma_dict = pma_nw_node_dict(pma_nw_file_path)

    # Creating File which we will have in Output
    logging.info("Creating Object for output Excel ")
    writer = pd.ExcelWriter(Output_File, engine='openpyxl')
    book = openpyxl.load_workbook(Template_file)
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    # Loading template in pandas dataframe
    logging.info("Reading Input Template file")
    template_df_map = pd.read_excel(Template_file, sheet_name=None)

    # Generating Dictionary after reading and parsing node types directories
    # based on nedate and its corresponding Inp file
    logging.info("Creating dictionary of all node types after parsing ini files")
    parsed_hash = main()

    # Iterating each node type for Update individual output sheet
    for key, values in parsed_hash.items():
        opco = key
        print(opco)

        # Continue if opco is commented in pma_nw-final.cong
        if opco.lower() not in updated_pma_dict.keys():
            continue

        # # ------------------
        # if 'SDP' == opco.upper():
        #     sheet_name = "SDP(Daily)"
        #     final_data = nodes_iterator_sdp(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )
        # # ------------------
        # if 'AIR' == opco.upper():
        #     sheet_name = "AIR(Daily)"
        #     final_data = nodes_iterator_air(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )

        # # ------------------
        # if 'OCC' == opco.upper():
        #     sheet_name = "vOCC"
        #     final_data = nodes_iterator_occ(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )

        #         # ------------------
        # if 'SAPC' == opco.upper():
        #     sheet_name = "SAPC"
        #     final_data = nodes_iterator_sapc(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )

        # # ------------------
        # if 'CCN' == opco.upper():
        #     sheet_name = "CCN(Daily)"
        #     final_data = nodes_iterator_ccn(values, updated_pma_dict[opco.lower()])

        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )

        # # ------------------
        # if 'CCN' == opco.upper():
        #     sheet_name = "CCN"
        #     final_data = nodes_iterator_ccn(values, updated_pma_dict[opco.lower()])
        #     for index,row in template_df_map['CCN'].iterrows():
        #         for inner_row in final_data:
        #             if (str(row['IO2 IP']) in str(inner_row['IP Address']) and 
        #                 inner_row['Daily sheduled DBN backup'] == 'Done'):
                        
        #                 template_df_map['CCN'].loc[index, ['DBN backup(Daily)']]=day_DD_MON_YYYY
        #                 break
        #     print(template_df_map['CCN'])
        #     template_df_map['CCN'].to_excel(writer, sheet_name=sheet_name,index=False)


            # # ------------------
            # writer.save()
            # exit()
            # template_df_map = append_row_to_excel(
            #     writer, template_df_map, final_data, sheet_name
            # )

        # # ------------------

        # # ------------------
        # if 'EMA' == opco.upper():
        #     sheet_name = "EMA"
        #     final_data = nodes_iterator_ema(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )
        
        # # ------------------
        # if 'NGVS' == opco.strip().upper():
        #     sheet_name = "NGVS"
        #     final_data = nodes_iterator_ngvs(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )

        # ------------------
        # if 'VS' == opco.upper():
        #     sheet_name = "NGCRS Backup"
        #     final_data = nodes_iterator_vs(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )

        # # ------------------
        # if 'CRS' == opco.upper():
        #     sheet_name = "CRS DB backup"
        #     final_data = nodes_iterator_crs(values, updated_pma_dict[opco.lower()])
        #     template_df_map = append_row_to_excel(
        #         writer, template_df_map, final_data, sheet_name
        #     )


        # ------------------
        if 'VCCN' == opco.upper():
            sheet_name = "VCCN_Daily"
            final_data, success_nodes = nodes_iterator_vccn(
                values, updated_pma_dict[opco.lower()]
                )
            total_nodes = len(final_data)
            # template_df_map[sheet_name].loc[1,'C'] = 2
            writer.sheets[sheet_name].cell(1,3).value  = day_DD_MON_YYYY
            writer.sheets[sheet_name].cell(2,3).value  = total_nodes
            writer.sheets[sheet_name].cell(3,3).value  = total_nodes-success_nodes
            writer.sheets[sheet_name].cell(4,3).value  = success_nodes


            final_data = pd.DataFrame (final_data)
            template_df_map[sheet_name] = final_data
            template_df_map[sheet_name].to_excel(
                writer, sheet_name, index=False, startrow=6,startcol=0, header=False
                )





    # # Flattening Json and return a list of nodes of NotDone cases for Logs sheet.
    # logging.info("Flatting Dataframe")
    # log_rows = json_flatten_for_logs(parsed_hash, updated_pma_dict, Base_path)

    # logging.info("Writting Data to Logs sheet in output excel file")
    # if len(log_rows) > 0:
    #     template_df_map['Logs'] = template_df_map['Logs'] \
    #         .append(log_rows, ignore_index=True)

    #     template_df_map['Logs'].to_excel(
    #         writer, 'Logs', index=False, startrow=1, startcol=0, header=False
    #     )

    print("===================================")
    print(template_df_map["VCCN_Daily"])
    print("===================================")
    writer.save()
    logging.info("Sending mail")
    flag=False
    # Send_Email_SMTP(Output_File,flag)
except Exception as error:
    raise
    logging.error("Error Occured: {}".format(error))
    logging.info("Sending Failier mail")
    flag=True
    # Send_Email_SMTP(log_file_path,flag)
logging.info("Automation Ended")
print("Process Ended")

