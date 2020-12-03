import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

import openpyxl
import pandas as pd
from updated import *
import ccn


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
                    geo_flag = 0
                    if 'Success' not in values3 and 'Password Issue' not in values3 :
                        if key.lower() not in updated_pma_dict:
                            if "geo-red" not in key.lower():
                                continue
                        if "geo-red"  in key.lower():
                            if "sdp" in key.lower():
                                key = "sdp"
                            if "ngvs" in key.lower():
                                key = "ngvs"
                            geo_flag = 1
                        else:
                            flag = Is_IP_Exists(key2, updated_pma_dict[key.lower()])
                            if not flag:
                                continue


                        if geo_flag == 1 and key.lower()=="sdp":
                            # print(key, key1, key2, full_path,"=======================","in sDP")
                            dynamic_path = '{}/{}_{}/{}'.format(key, key2, key1, "TTMonitorStandby.inp")
                            full_path = basepath + dynamic_path
                            file_data = read_file(full_path)
                            geo_str = file_data.strip().split('\n')
                            arr_len = len(geo_str)
                            if arr_len > 4:
                                file_data = read_file_encoaded(full_path)
                                log_row = ["SDP-GEO-RED", key1, key2, "TTMonitorStandby.inp", file_data]
                                log_rows.append(log_row)

                            dynamic_path = '{}/{}_{}/{}'.format(key, key2, key1, "TTMonitorlog.inp")
                            full_path = basepath + dynamic_path
                            file_data = read_file_encoaded(full_path)
                            if '9' not in file_data:
                                log_row = ["SDP-GEO-RED", key1, key2, "TTMonitorlog.inp", file_data]
                                log_rows.append(log_row)
                            continue

                        if geo_flag == 1 and key.lower()=="ngvs":
                            # print("pppppppppppppppppxxxxxxxxxx iam in ",geo_flag,key)
                            dynamic_path = '{}/{}_{}/{}'.format(key, key2, key1, "geo.inp")
                            full_path = basepath + dynamic_path
                            file_data = read_file(full_path)
                            status = ngvs_geo(file_data)
                            if 'Success' not in status:
                                log_row = ["NGVS-GEO-RED", key1, key2, "geo.inp", file_data]
                                log_rows.append(log_row)
                            continue
                        if geo_flag == 0 and key.lower()=="ngvs":
                            print(key3,"]]]]]]]]]]]]]")
                            dynamic_path = '{}/{}_{}/'.format(key, key2, key1)
                            full_path = basepath + dynamic_path
                            log_row = ["NGVS-GEO-RED", key1, key2]
                            print(ngvs_cassendra_logs(full_path,log_row))
                            logs = ngvs_cassendra_logs(full_path,log_row)
                            for log in logs:
                                log_rows.append(log)


                          

                        dynamic_path = '{}/{}_{}/{}'.format(key, key2, key1, key3)
                        full_path = basepath + dynamic_path
                        try:
                            file_data = read_file_encoaded(full_path)
                        except Exception as e:
                            continue
                        log_row = [key, key1, key2, key3, file_data]
                        log_rows.append(log_row)
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


def nodes_iterator_sdp(values, pma_ips):
    """
        Iterate over each node name of sdp and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet
    """
    final_data = []
    success_nodes = 0 
    success_nodes_without_pair = 0 
    for key, value in values.items():
        IP1, IP2 = list(value.keys())
        flag = Is_IP_Exists(IP1, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name)
        if int(IP1.split('.')[-1]) > int(IP2.split('.')[-1]):
            row_data.append(IP2)
            row_data.append(IP1)
            status1 = update_status(list(value[IP1].values())[0])
            status = update_status(list(value[IP2].values())[0])
        else:
            row_data.append(IP1)
            row_data.append(IP2)
            status1 = update_status(list(value[IP2].values())[0])
            status = update_status(list(value[IP1].values())[0])
        row_data.append(status)
        row_data.append(status1)
        if ('not' not in status.lower() and 'Issue' not in status ):
            success_nodes += 1
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes_without_pair += 1
        if 'not' not in status1.lower()  and 'Issue' not in status1:
            success_nodes_without_pair += 1
        final_data.append(row_data)
    return final_data, success_nodes, success_nodes_without_pair



def nodes_iterator_air(values, pma_ips):
    """
        Iterate over each node name of air and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes = 0 
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name.upper())
        row_data.append(IP)
        temp_status = list(list(value.values())[0].values())[0]
        status = update_status(temp_status)
        row_data.append(status)
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes += 1
        final_data.append(row_data)
    return final_data, success_nodes


def nodes_iterator_ngvs_geo(values, pma_ips):
    """
        Iterate over each node name of ema and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes = 0
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name) # node name
        row_data.append(IP)        #Ip
        status = list(list(value.values())[0].values())[0]
        row_data.append(status)    #VCCN Backup Status
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes += 1
        final_data.append(row_data)
    return final_data, success_nodes

def nodes_iterator_sdp_geo(values, pma_ips):
    """
        Iterate over each node name of ema and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes = 0 
    for key, value in values.items():
        IP1, IP2 = list(value.keys())
        flag = Is_IP_Exists(IP1, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name)
        row_data.append(IP1)
        status = update_status(list(value[IP1].values())[0])
        row_data.append(status)
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes += 1
        final_data.append(row_data)

        row_data = []
        row_data.append(node_name)
        row_data.append(IP2)
        status1 = update_status(list(value[IP2].values())[0])
        row_data.append(status1)
        if 'not' not in status1.lower() and 'Issue' not in status1:
            success_nodes += 1
        final_data.append(row_data)

    return final_data, success_nodes
    


def nodes_iterator_ngvs(values, pma_ips):
    """
        Iterate over each node name of ema and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes_cassendra = 0
    success_nodes_tape = 0
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name) # node name
        row_data.append(IP)        #Ip
        status = update_status(list(value.values())[0]['tape.inp'])
        row_data.append(status)    #VCCN Backup Status
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes_tape += 1
        status = update_status(list(value.values())[0]['cassendra.inp'])
        row_data.append(status)    #VCCN Backup Status
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes_cassendra += 1
        final_data.append(row_data)
    return final_data, success_nodes_cassendra, success_nodes_tape

def nodes_iterator_vccn(values, pma_ips):
    """
        Iterate over each node name of ema and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes = 0
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name) # node name
        row_data.append(IP)        #Ip
        status = update_status(list(value.values())[0]['Vccn_config_backup.inp'])
        row_data.append(status)    #VCCN Backup Status
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes += 1
        final_data.append(row_data)
    return final_data, success_nodes


def nodes_iterator_ccn(values, pma_ips):
    """
        Iterate over each node name of ccn and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes = 0
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name)
        if node_name.upper() in ccn.ccn_list:
            row_data.extend(ccn.ccn_list[node_name.upper()])
        row_data.insert(-2, IP)
        status = update_status(list(list(value.values())[0].values())[0])
        row_data.append(status)
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes += 1
        final_data.append(row_data)
    return final_data, success_nodes


def nodes_iterator_occ(values, pma_ips):
    """
        Iterate over each node name of occ and check if the ip exist in
        pma_nw_final.conf file and create a list of node to insert in
        final output excel sheet with their corresponding headers
    """
    final_data = []
    success_nodes = 0
    for key, value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = []
        node_name = key
        row_data.append(node_name.upper())   #Server name
        temp_status = list(list(value.values())[0].values())[0]
        status = update_status(temp_status)
        if 'OJO' in node_name.upper():
            row_data.append('Ojota')
        if 'AB' in node_name.upper():
            row_data.append('ABUJA')
        if 'AS' in node_name.upper():
            row_data.append('ASABA')
        row_data.append(IP)                  #ip
        row_data.append(status)
        if 'not' not in status.lower() and 'Issue' not in status:
            success_nodes += 1
        # row_data['Failed Reason (If any)'] = temp_status.split('^^')[-1]
        final_data.append(row_data)
    return final_data, success_nodes


def append_row_to_excel(writer, template_df_map, final_data, sheet_name):
    """
        This function append row to excel sheet and save the resultant to 
        output excel sheet . 
    """
    for row in final_data:
        template_df_map[sheet_name] = template_df_map[sheet_name].append(row, ignore_index=True)
    template_df_map[sheet_name].to_excel(writer, sheet_name, index=False)
    return template_df_map


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


def ngvs_cassendra_logs(basepath, cass_log_row):                    
    status = ''
    fail_reason = ''
    logs = []
    inp_array = ['cassendra1.inp','cassendra2.inp','cassendra3.inp']
    for inp_file_name in inp_array:
        full_path = basepath + inp_file_name
        file_data = read_file_encoaded(full_path)
        temp_row = cass_log_row[:]
        temp_row.append(inp_file_name)
        temp_row.append(file_data)
        logs.append(temp_row)
    return logs


def Send_Email_SMTP(Attachment_Full_Path, flag):
    subject = 'New MTN Backup Tracker for SouthAfrica'
    text = 'New MTN Backup Tracker for SouthAfrica'
    fromaddr = 'no-reply@AutoBOT'
    if flag == False:
        toaddr = ['akash.a.agrawal@ericsson.com', 'akshath.sharma@ericsson.com', 'aditya.k.kumar@ericsson.com']
    else:
        toaddr = ['akash.a.agrawal@ericsson.com', 'akshath.sharma@ericsson.com']
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
