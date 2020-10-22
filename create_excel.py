from updated import *
import pandas as pd
import openpyxl


def update_status(status):
    if 'Success' in status:
        return "Done"
    elif 'Fail' in status:
        return "Not Done"
    else:
        return status

def nodes_iterator_air(values):
    final_data = []
    for key , value in values.items():
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        IP = list(value.keys())[0]
        row_data['IP  Address'] = IP
        temp_status = list(list(value.values())[0].values())[0]
        status = update_status(temp_status)
        # if 'Password Issue' in temp_status:
        #     status = 'Not Done'
        #     row_data['Failed Reason (If any)'] = temp_status
        row_data['Tape Backup Status'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data

def nodes_iterator_ccn(values):
    final_data = []
    for key , value in values.items():
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        IP = list(value.keys())[0]
        row_data['IP  Address'] = IP
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['Daily sheduled DBN backup'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data

def nodes_iterator_sdp(values):
    final_data = []
    for key , value in values.items():
        row_data = {}
        node_name = key
        row_data[26] = node_name
        IP = list(value.keys())[0]
        row_data['IP  Address'] = IP
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['Tape Backup Status'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data


def nodes_iterator_occ(values):
    final_data = []
    for key , value in values.items():
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        IP = list(value.keys())[0]
        row_data['IP  Address'] = IP
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['FS Backup Status'] = status
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data
        

def nodes_iterator_ngvs(values):
    final_data = []
    for key , value in values.items():
        row_data = {}
        node_name = key
        row_data['Node Name  '] = node_name
        IP = list(value.keys())[0]
        row_data['Node IP'] = IP
        status = update_status(list(list(value.values())[0].values())[0])
        row_data['DB dump status '] = status
        status1 = update_status(list(list(value.values())[0].values())[0])
        row_data['FS dump status'] = status1
        final_data.append(row_data)
        print(opco, node_name, IP, status)
    return final_data
        








Output_File = '/home/ubuntu/perl-to-python/TEMP/MTN -Congo_backup_tracker_OUT.xlsx' 
Output_File1 = '/home/ubuntu/perl-to-python/TEMP/MTN -Congo_backup_tracker_OUT1.xlsx' 

writer = pd.ExcelWriter(Output_File1, engine='openpyxl')
book = openpyxl.load_workbook(Output_File)
writer.book = book
writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
template_to_df_map = pd.read_excel(Output_File, sheet_name=None)



        
parsed_hash = main()
for key, values in parsed_hash.items():
    opco = key
    if opco.upper() ==  'AIR':
        final_data = nodes_iterator_air(values)
        for row in final_data:
            print(row)
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        print("------------------------")
        template_to_df_map['AIR'].to_excel(writer, 'AIR', index=False)

    if opco.upper() ==  'CCN':
        final_data = nodes_iterator_ccn(values)
        for row in final_data:
            print(row)
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        print("------------------------")
        template_to_df_map['CCN'].to_excel(writer, 'CCN', index=False)

    if opco.upper() ==  'SDP':
        final_data = nodes_iterator_sdp(values)
        for row in final_data:
            print(row)
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        print("------------------------")
        template_to_df_map['SDP'].to_excel(writer, 'SDP', index=False)


    if opco.upper() ==  'OCC':
        final_data = nodes_iterator_occ(values)
        for row in final_data:
            print(row)
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        print("------------------------")
        template_to_df_map['OCC'].to_excel(writer, 'OCC', index=False)


    if opco.upper() ==  'NGVS':
        final_data = nodes_iterator_ngvs(values)
        for row in final_data:
            print(row)
            template_to_df_map['NGVS'].dropna(subset=['Node IP'],   inplace=True) # removing the empty row 
            template_to_df_map[opco.upper()] =template_to_df_map[opco.upper()].append(row,  ignore_index = True) 
        print("------------------------")
        template_to_df_map['NGVS'].to_excel(writer, 'NGVS', index=False)




print("===================================")
print(template_to_df_map['NGVS'])
print("===================================")
writer.save()

