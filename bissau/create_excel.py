import logging
from datetime import date
from datetime import datetime

import openpyxl
import pandas as pd
from utils import *

print("Process Started")
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

        # Continue if opco is commented in pma_nw-final.cong
        if opco.lower() not in updated_pma_dict.keys():
            continue

        # ------------------
        logging.info("Writting data for OPCO : {}".format(opco))
        if 'SDP' == opco.upper():
            sheet_name = "SDP"
            final_data = nodes_iterator_sdp(values, updated_pma_dict[opco.lower()])
            temp_pd = template_df_map[sheet_name].columns
            template_df_map[sheet_name].columns = template_df_map[sheet_name].iloc[0]
            template_df_map[sheet_name] = template_df_map[sheet_name].reset_index(drop=True)
            for row in final_data:
                template_df_map[sheet_name].dropna(subset=['Node Name'], inplace=True)
                template_df_map[sheet_name] = template_df_map[sheet_name].append(row, ignore_index=True)
            # template_df_map = template_df_map.sort_values('Node Name')
            template_df_map[sheet_name].columns = temp_pd
            template_df_map[sheet_name].to_excel(
                writer, sheet_name,
                index=False, startrow=1,
                startcol=0, header=False
            )

        # ------------------
        if 'AIR' == opco.upper():
            sheet_name = "AIR"
            final_data = nodes_iterator_air(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )

        # ------------------
        if 'CCN' == opco.upper():
            sheet_name = "CCN"
            final_data = nodes_iterator_ccn(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )

        # ------------------
        if 'VS' == opco.upper():
            sheet_name = "VS Daily"
            final_data = nodes_iterator_vs(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )

        # ------------------
        if 'CRS' == opco.upper():
            sheet_name = "CRS DB backup"
            final_data = nodes_iterator_crs(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )


        # ------------------
        if 'MINSAT' == opco.upper():
            sheet_name = "Minsat_Daily"
            final_data = nodes_iterator_minsat(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )


        # ------------------
        if 'EMA' == opco.upper():
            sheet_name = "EMA proclogs_Backup"
            final_data = nodes_iterator_ema(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )

                # ------------------
        if 'OCC' == opco.upper():
            sheet_name = "OCC"
            final_data = nodes_iterator_occ(values, updated_pma_dict[opco.lower()])
            template_df_map = append_row_to_excel(
                writer, template_df_map, final_data, sheet_name
            )

    # Flattening Json and return a list of nodes of NotDone cases for Logs sheet.
    logging.info("Flatting Dataframe")
    log_rows = json_flatten_for_logs(parsed_hash, updated_pma_dict, Base_path)

    logging.info("Writting Data to Logs sheet in output excel file")
    if len(log_rows) > 0:
        template_df_map['Logs'] = template_df_map['Logs'] \
            .append(log_rows, ignore_index=True)

        template_df_map['Logs'].to_excel(
            writer, 'Logs', index=False, startrow=1, startcol=0, header=False
        )

    print("===================================")
    print(template_df_map["OCC"])
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
