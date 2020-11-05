import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import openpyxl
import pandas as pd
from updated import *





def pma_nw_node_dict(pma_nw_file_path):
    """
        Function will read pma_nw_final.conf anc return a dict with opco as
        key and node ip list as values .
    """
    updated_pma_dict = {}
    config = ConfigParser()
    config.read(pma_nw_file_path)
    pma_dict = dict(config.items('3_nodeip'))
    for key, value in pma_dict.items():
        new_key = key.split('-')[-1]
        new_value = value.split(',')
        updated_pma_dict[new_key] = new_value
    return updated_pma_dict


def password_issue(temp_status, row_data):
    status = 'Not Done'
    try:
        row_data['Failed Reason (If any)'] = temp_status
    except:
        row_data['Remarks'] = temp_status
    return status, row_data


def update_status(status):
    """
        Function check the status success or Fails and return Done or Not Done
        Corresponds to status
    """
    if 'Success' in status:
        return "Done"
    elif 'Fail' in status:
        return "Not Done"
    else:
        return status


def Is_IP_Exists(IP, pma_ips):
    """
        Function check if the IP exist in pma_nw_final.conf and return True if
        exist otherwise return False
    """
    flag = False
    for row in pma_ips:
        if IP in row:
            flag = True
            break
    return flag


def json_flatten_for_logs(parsed_hash, updated_pma_dict, basepath):
    """
        Flattening Json and return a list of nodes having not done cases
        with its .inp file Data.
    """
    log_rows = []
    for key, values in parsed_hash.items():
        for key1, values1 in values.items():
            for key2, values2 in values1.items():
                for key3, values3 in values2.items():
                    if 'Success' not in values3:
                        if key.lower() not in updated_pma_dict:
                            continue
                        flag = Is_IP_Exists(key2, updated_pma_dict[key.lower()])
                        if not flag:
                            continue
                        dynamic_path = '{}/{}_{}/{}'.format(key, key2, key1, key3)
                        full_path = basepath + dynamic_path
                        file_data = read_file(full_path)
                        log_row = [key, key1, key2, key3, file_data]
                        log_rows.append(log_row)
    # print(key,key1,key2,key3,values3)
    # occ pnrocc2 10.52.160.39 fs_occ_backup.inp Connectivity/Password Issue
    return log_rows


def excel_summary_writer(template_to_df_map, writer):
    """
        This function write Dataframe data to excel Summary sheet.
    """
    template_to_df_map['AIR'].to_excel(
        writer, 'Summary', index=False, startrow=1, startcol=1, header=False
    )
    template_to_df_map['SDP'].to_excel(
        writer, 'Summary', index=False, startrow=6, startcol=1, header=False
    )
    template_to_df_map['CCN'].to_excel(
        writer, 'Summary', index=False, startrow=11, startcol=1, header=False
    )
    template_to_df_map['NGVS'].to_excel(
        writer, 'Summary', index=False, startrow=14, startcol=1, header=False
    )
    template_to_df_map['MINSAT'].to_excel(
        writer, 'Summary', index=False, startrow=21, startcol=1, header=False
    )
    template_to_df_map['EMA'].to_excel(
        writer, 'Summary', index=False, startrow=24, startcol=1, header=False
    )
    template_to_df_map['OCC'].to_excel(
        writer, 'Summary', index=False, startrow=27, startcol=1, header=False
    )
    return writer


def nodes_iterator_air(values, pma_ips):
    """
        Iterate over each node name of air and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []

    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name'] = node_name
        row_data['IP Address'] = IP
        temp_status = list(list(value.values())[0].values())[0]
        status = update_status(temp_status)
        # if 'Password Issue' in temp_status:
        #     status, rowdata = password_issue(temp_status, row_data)
        row_data['Backup Status'] = status
        final_data.append(row_data)
    return final_data


def nodes_iterator_vs(values, pma_ips):
    """
        Iterate over each node name of air and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name'] = node_name
        row_data['Hostname'] = IP
        status = update_status(list(value.values())[0]['nfs.inp'])
        row_data['NFS Backup status'] = status
        status = update_status(list(value.values())[0]['ora.inp'])
        row_data['OraBackup'] = status
        status = update_status(list(value.values())[0]['ora_archive.inp'])
        row_data['OraArchiveBackup taken on Storage'] = status

        # if 'Password Issue' in temp_status:
        #     status, rowdata = password_issue(temp_status, row_data)
        final_data.append(row_data)
    return final_data

def nodes_iterator_crs(values, pma_ips):
        """
            Iterate over each node name of air and check if the ip exist in
            pma_nw_final.conf file and create a list of node to insert in
            final output excel sheet with their corresponding headers
        """
        final_data = []
        for key, value in values.items():
            IP = list(value.keys())[0]
            flag = Is_IP_Exists(IP, pma_ips)
            if not flag:
                continue
            row_data = {}
            node_name = key
            row_data['Node Name'] = node_name
            row_data['Node IP'] = IP
            status = update_status(list(value.values())[0]['db.inp'])
            row_data['CRS DB Backup _ Daily'] = status
            # if 'Password Issue' in temp_status:
            #     status, rowdata = password_issue(temp_status, row_data)
            final_data.append(row_data)
        return final_data


def nodes_iterator_ccn(values, pma_ips):
    """
        Iterate over each node name of ccn and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        row_data['IP Address'] = IP
        node_name = key
        row_data['Node Name'] = node_name
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['Daily sheduled DBN backup'] = status
        final_data.append(row_data)
    return final_data


def nodes_iterator_sdp(values, pma_ips):
    """
        Iterate over each node name of sdp and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet
    """
    final_data = []
    for key, value in values.items():
        IP1, IP2 = list(value.keys())
        # flag = Is_IP_Exists(IP, pma_ips)
        # if not flag:
        #     continue
        row_data = {}
        node_name = key
        row_data['Node Name'] = node_name
        if int(IP1.split('.')[-1]) > int(IP2.split('.')[-1]):
            row_data['Node B-IP'] = IP1
            row_data['Node A-IP'] = IP2
        else:
            row_data['Node A-IP'] = IP1
            row_data['Node B-IP'] = IP2
        status1 = update_status(list(list(value.values())[0].values())[0])
        row_data['Node - A'] = status1
        status2 = update_status(list(list(value.values())[1].values())[0])
        row_data['Node - B'] = status2
        final_data.append(row_data)
    return final_data



def nodes_iterator_sdp_geo(values, pma_ips):
    """
        Iterate over each node name of occ and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    for key, value in values.items():
        # IP1, IP2 = list(value.keys())
        IP1, IP2 = list(value.keys())
        sorted_list = []
        if int(IP1.split('.')[-1]) > int(IP2.split('.')[-1]):
            sorted_list = [IP1, IP2]
        else:
            sorted_list = [IP2, IP1]

        for index in range(len(sorted_list)):
            row_data = {}
            node_name = key
            row_data['Hostname'] = node_name+str(index+1)
            status = update_status(list(value[sorted_list[index]].values())[0])
            row_data['Todays_date'] = status
            final_data.append(row_data)
    return final_data



def nodes_iterator_occ(values, pma_ips):
    """
        Iterate over each node name of occ and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        row_data['IP  Address'] = IP
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['FS Backup Status'] = status
        final_data.append(row_data)
    return final_data


def nodes_iterator_ngvs(values, pma_ips):
    """
        Iterate over each node name of ngvs and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """

    final_data = []
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        row_data['Node IP'] = IP
        status = update_status(list(value.values())[0]['fs.inp'])
        row_data['DB dump status '] = status
        status1 = update_status(list(value.values())[0]['db3.inp'])
        row_data['FS dump status'] = status1
        final_data.append(row_data)
    return final_data


def nodes_iterator_minsat(values, pma_ips):
    """
        Iterate over each node name of minsat and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name'] = node_name
        row_data['Node IP'] = IP
        status = update_status(list(value.values())[0]['db.inp'])
        row_data['Daily DB dump status at Storage'] = status
        status = update_status(list(value.values())[0]['fs.inp'])
        row_data['Daily FS dump status at Tape'] = status
        final_data.append(row_data)
    return final_data


def nodes_iterator_ema(values, pma_ips):
    """
        Iterate over each node name of ema and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name'] = node_name
        row_data['Node IP'] = IP
        status = update_status(list(value.values())[0]['proclog.inp'])
        row_data['EMA proclogs_Backup'] = status
        status1 = update_status(list(value.values())[0]['sogconfig.inp'])
        row_data['SOG Config'] = status1
        final_data.append(row_data)
    return final_data



def get_dynamic_function_dict():
    """
        returning mapping for dynamic function calling
    """
    mapping = {
        "nodes_iterator_air": nodes_iterator_air,
        "nodes_iterator_ccn": nodes_iterator_ccn,
        "nodes_iterator_sdp": nodes_iterator_sdp,
        "nodes_iterator_occ": nodes_iterator_occ,
        "nodes_iterator_ngvs": nodes_iterator_ngvs,
        "nodes_iterator_minsat": nodes_iterator_minsat,
        "nodes_iterator_ema": nodes_iterator_ema,
        "nodes_iterator_crs": nodes_iterator_crs
    }
    return mapping


def Send_Email_SMTP(Attachment_Full_Path):
    subject = 'New MTN Backup Tracker for Congo'  # + GetOpco_Name(opco)
    text = 'New MTN Backup Tracker for Congo'  # + GetOpco_Name(opco)
    fromaddr = 'no-reply@AutoBOT'
    # toaddr = ['gnoc.1st.la.mtn.rsaa@ericsson.com','PDLMTNFMIN@pdl.internal.ericsson.com','PDLFOINMTN@pdl.internal.ericsson.com','PDLHIFTMAN@pdl.internal.ericsson.com']
    toaddr = ['akash.a.agrawal@ericsson.com', 'akshath.sharma@ericsson.com', 'aditya.k.kumar@ericsson.com']
    COMMASPACE = ', '

    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = COMMASPACE.join(toaddr)
    msg['Subject'] = subject

    body = text

    msg.attach(MIMEText(body, 'plain'))

    part = MIMEBase('application', 'octet-stream')

    part.set_payload(open(Attachment_Full_Path, "rb").read())

    encoders.encode_base64(part)
    filename = Attachment_Full_Path.split('/')[-1]
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)
    text = msg.as_string()

    try:
        smtpObj = smtplib.SMTP('172.23.168.13', 25)
        smtpObj.sendmail(fromaddr, toaddr, text)
        print("Successfully sent email")
    except smtplib.SMTPException:
        print("Error: unable to send email")
