from updated import *
import pandas as pd
import openpyxl
try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0



def password_issue(temp_status, row_data):
    status = 'Not Done'
    try:
        row_data['Failed Reason (If any)'] = temp_status
    except:
        row_data['Remarks'] = temp_status
    return status, row_data


def update_status(status):
    if 'Success' in status:
        return "Done"
    # else:
    #     return "Not Done"
    elif 'Fail' in status:
        return "Not Done"
    else:
        return status

def Is_IP_Exists(IP, pma_ips):
    flag = False
    for row in pma_ips:
        if IP in row:
            flag = True
            break
    return flag

def nodes_iterator_air(values,pma_ips):
    final_data = []
    for key , value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        row_data['IP  Address'] = IP
        temp_status = list(list(value.values())[0].values())[0]
        status = update_status(temp_status)
        # if 'Password Issue' in temp_status:
        #     status, rowdata = password_issue(temp_status, row_data)
        row_data['Tape Backup Status'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data

def nodes_iterator_ccn(values, pma_ips):
    final_data = []
    for key , value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        row_data['IP  Address'] = IP
        node_name = key
        row_data['Node Name  '] = node_name
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['Daily sheduled DBN backup'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data

def nodes_iterator_sdp(values, pma_ips):
    final_data = []
    for key , value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data[26] = node_name
        row_data['IP  Address'] = IP
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['Tape Backup Status'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data


def nodes_iterator_occ(values, pma_ips):
    final_data = []
    for key , value in values.items():
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
        print(opco, node_name, IP, status)
    return final_data
        

def nodes_iterator_ngvs(values, pma_ips):
    final_data = []
    for key , value in values.items():
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
        print(opco, node_name, IP, status)
    return final_data
        


def nodes_iterator_minsat(values, pma_ips):
    final_data = []
    for key , value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Hostname'] = node_name
        row_data['Node IP'] = IP
        status = update_status(list(value.values())[0]['fs.inp'])
        row_data['Daily DB dump status'] = status
        status1 = update_status(list(value.values())[0]['db_backup.inp'])
        row_data['Daily FS dump status'] = status1
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data



def nodes_iterator_ema(values, pma_ips):
    final_data = []
    for key , value in values.items():
        IP = list(value.keys())[0]
        flag = Is_IP_Exists(IP, pma_ips)
        if not flag:
            continue
        row_data = {}
        node_name = key
        row_data['Node Name'] = node_name
        row_data['Node IP'] = IP
        status = update_status(list(value.values())[0]['proclog.inp'])
        row_data['Proclogs_Backup status'] = status
        status1 = update_status(list(value.values())[0]['config_backup.inp'])
        row_data['Config_Backup status'] = status1
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data
        




config = ConfigParser()
config.read('pma_nw_final.conf')
pma_dict = dict(config.items('3_nodeip'))
updated_pma_dict = {}
for key, value in pma_dict.items():
    new_key = key.split('-')[-1]
    new_value = value.split(',')
    updated_pma_dict[new_key]= new_value


Output_File = '/home/ubuntu/perl-to-python/TEMP/MTN -Congo_backup_tracker_OUT.xlsx' 
Output_File1 = '/home/ubuntu/perl-to-python/TEMP/MTN -Congo_backup_tracker_OUT1.xlsx' 

writer = pd.ExcelWriter(Output_File1, engine='openpyxl')
book = openpyxl.load_workbook(Output_File)
writer.book = book
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
template_to_df_map = pd.read_excel(Output_File, sheet_name=None)




parsed_hash = main()
print(pma_dict.keys())
for key, values in parsed_hash.items():
    opco = key

    if opco.lower() not in updated_pma_dict.keys():
        '''Continue if opco is commented in pma_nw-final.cong'''
        continue



    '''
        final_data = 'nodes_iterator_'+opco.lower()(values)
        for row in final_data:
            try:
                template_to_df_map[opco.upper()].dropna(subset=['Node IP'],   inplace=True) # removing the empty row 
            except:
                pass
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map[opco.upper()].to_excel(writer, opco.upper(), index=False)
    '''
    if opco.upper() ==  'AIR':
        final_data = nodes_iterator_air(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['AIR'].to_excel(writer, 'AIR', index=False)

    if opco.upper() ==  'CCN':
        final_data = nodes_iterator_ccn(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['CCN'].to_excel(writer, 'CCN', index=False)

    if opco.upper() ==  'SDP':
        final_data = nodes_iterator_sdp(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['SDP'].to_excel(writer, 'SDP', index=False)


    if opco.upper() ==  'OCC':
        final_data = nodes_iterator_occ(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['OCC'].to_excel(writer, 'OCC', index=False)


    if opco.upper() ==  'NGVS':
        final_data = nodes_iterator_ngvs(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map['NGVS'].dropna(subset=['Node IP'],   inplace=True) # removing the empty row 
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['NGVS'].to_excel(writer, 'NGVS', index=False)


    if opco.upper() ==  'MINSAT':
        final_data = nodes_iterator_minsat(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map['MINSAT'].dropna(subset=['Node IP'],   inplace=True) # removing the empty row 
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['MINSAT'].to_excel(writer, 'MINSAT', index=False)

    if opco.upper() ==  'EMA':
        final_data = nodes_iterator_ema(values,updated_pma_dict[opco.lower()])
        for row in final_data:
            template_to_df_map['EMA'].dropna(subset=['Node IP'],   inplace=True) # removing the empty row 
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        template_to_df_map['EMA'].to_excel(writer, 'EMA', index=False)


    template_to_df_map['AIR'].to_excel(writer, 'Summary', index=False, startrow=1,startcol=1, header=False)
    template_to_df_map['SDP'].to_excel(writer, 'Summary', index=False, startrow=6,startcol=1, header=False)
    template_to_df_map['CCN'].to_excel(writer, 'Summary', index=False, startrow=11,startcol=1, header=False)
    template_to_df_map['NGVS'].to_excel(writer, 'Summary', index=False, startrow=14,startcol=1, header=False)
    template_to_df_map['MINSAT'].to_excel(writer, 'Summary', index=False, startrow=21,startcol=1, header=False)
    template_to_df_map['EMA'].to_excel(writer, 'Summary', index=False, startrow=24,startcol=1, header=False)
    template_to_df_map['OCC'].to_excel(writer, 'Summary', index=False, startrow=27,startcol=1, header=False)

print("===================================")
print(template_to_df_map['AIR'])
print("===================================")
writer.save()

