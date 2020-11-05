import logging
from datetime import date

import openpyxl
import pandas as pd
from utils import *


print("Process Started")
# Initialsing Loggine module
log_file_path = "./logs/logs_{}.log".format(str(date.today()))
logging.basicConfig(
    level=logging.INFO,
    # filename=log_file_path
)
logging.info("Starting Automation...")

# Loading config.ini file into a dictionary
logging.info("Loading Config.ini")
config_data = load_config_ini()

# mapping for dynamic function calling
logging.info("Loading Dynamic Function mapping")
mapping = get_dynamic_function_dict()

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
    logging.info("Loading Configations from pma_nw_file_path.conf")
    updated_pma_dict = pma_nw_node_dict(pma_nw_file_path)

    # Creating File which we will have in Output
    logging.info("Creating Object for outptu Excel ")
    writer = pd.ExcelWriter(Output_File, engine='openpyxl')
    book = openpyxl.load_workbook(Template_file)
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

    # Loading template in pandas dataframe
    logging.info("Reading Input Template file")
    template_to_df_map = pd.read_excel(Template_file, sheet_name=None)

    # Generating Dictionary after reading and parsing node types directories
    # based on nedate and its corresponding Inp file
    logging.info("Creating dictinary of all node types after parsing ini files")
    parsed_hash = main()

    # Iterating each node type for Update individual output sheet
    for key, values in parsed_hash.items():
        opco = key

        # Continue if opco is commented in pma_nw-final.cong
        if opco.lower() not in updated_pma_dict.keys():
            continue

        # calling nodes_iterators functions dynamically for its respective nodetype
        logging.info("Calling custom function for OPCO : {}".format(opco))
        custom_function = mapping['nodes_iterator_' + opco.lower()]
        final_data = custom_function(values, updated_pma_dict[opco.lower()])

        logging.info("Writting data for OPCO : {}".format(opco))
        for row in final_data:
            # removing the empty row from excel sheet
            try:
                template_to_df_map[opco.upper()].dropna(subset=['Node IP'], inplace=True)
            except:
                pass
            template_to_df_map[opco.upper()] = template_to_df_map[opco.upper()]\
                .append(row, ignore_index=True)

        # Writing Dataframe to its respective node type sheet in output excel file
        template_to_df_map[opco.upper()].to_excel(writer, opco.upper(), index=False)

        # create excel Summary sheet in outfile
        writer = excel_summary_writer(template_to_df_map, writer)

    # Flattening Json and return a list of nodes of NotDone cases for Logs sheet.
    logging.info("Flatting Dataframe")
    log_rows = json_flatten_for_logs(parsed_hash, updated_pma_dict, Base_path)

    logging.info("Writting Data to Logs sheet in output excel file")

    if len(log_rows)>0:
        template_to_df_map['Logs'] = template_to_df_map['Logs']\
        .append(log_rows, ignore_index=True)

        template_to_df_map['Logs'].to_excel(
            writer, 'Logs', index=False, startrow=1, startcol=0, header=False
         )

    # print("===================================")
    # print(template_to_df_map['AIR'])
    # print("===================================")
    writer.save()
    logging.info("Sending mail")
    # Send_Email_SMTP(Output_File)
except Exception as error:
    logging.error("Error Occured: {}".format(error))
    logging.info("Sending Failier mail")
    # Send_Email_SMTP(log_file_path)
logging.info("Automation Ended")
print("Process Ended")
