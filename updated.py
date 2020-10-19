import os
import re
# print(os.path.isdir("/home/el"))


def read_file(file_name):
    f = open(file_name,"r")
    file_data = f.read()
    f.close()
    return file_data

def set_users_conf():
    """Read pma_bkp_tracker.conf file and create dict."""
    users_details = {}
    conf_file = "conf/pma_bkp_tracker.conf"
    fh = open(conf_file, "r")
    data = fh.readlines()
    fh.close()
    for line in data:
        line = line.strip()
        key, values = line.split("=")
        users_details[key.strip()] = values.split(',')
    print(users_details)
    return users_details

from datetime import datetime


def read_opco_dir():
    basedir = "/home/ubuntu/perl-to-python/datasrc/mtnin/backuptracker/"
    child_dir = os.listdir(basedir)
    for inner_dir in child_dir:
        user_dir = basedir + inner_dir
        read_users_dir(user_dir, inner_dir)


def read_users_dir(user_dir, user):
    hosts = []
    if os.path.isdir(user_dir):
        hosts = os.listdir(user_dir)
    else:
        print("Can't open the current directory")
    for inp_dir in hosts:
        # $inp_dir_hash->{$user}->{$inp_dir} = 1; TODO : not getting this line
        inp_dir_path = user_dir + "/" + inp_dir
        read_inp(inp_dir_path, user, inp_dir) 


def read_inp(inp_dir_path, user, inp_dir):
    sdp_geo_check = 0
    sdp_geo = ''
    cassendra_arr = []
    cassandra_flag = 0

    ip, host = inp_dir.split("_")
    array_ref = users_details[user]

    user_l = user.lower().strip()

    inp_files = []
    if os.path.isdir(inp_dir_path):
        inp_files = os.listdir(inp_dir_path)
    else:
        print("Can't open the current directory")
    print(inp_files)

    # print(inp_files)

    inp_files2 = []
    for file in inp_files:
        if '.inp' in file:
            inp_files2.append(file)

    if user not in parsed_hash:
        parsed_hash[user] = {}
    if host not in parsed_hash[user]:
        parsed_hash[user][host] = {}
    if ip not in parsed_hash[user][host]:
        parsed_hash[user][host][ip] = {}

    if len(inp_files2) == 0:
        for array_ref1 in array_ref:
            parsed_hash[user][host][ip][array_ref1] = issue1
    else:
        nedate = read_file(inp_dir_path+"/nedate.inp")
        if curr_date2 in nedate:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = 'N/A'
            for inp_name in inp_files:
                inp_name = inp_name.strip()
                inp_file = "{}/{}".format(inp_dir_path, inp_name)
                file_data = read_file(inp_file)

                ##----------------- AIR Backup Check -----------------##
                if 'air' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'backup.inp' in inp_name:
                        status, fail_reason = tape(file_data, curr_date, curr_date5, inp_dir_path)
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason
                    

                ##----------------- MINSAT fs and db Check -----------------##
                if 'minsat' in user_l:
                    status = ''
                    fail_reason = ''

                    if 'fs.inp' in inp_name:
                        status = filesystem(file_data, curr_date6)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'db_backup.inp' in inp_name:
                        status = dbn(file_data, pre_date1, '')
                        parsed_hash[user][host][ip][inp_name] = status


                ##----------------- NGVS geo-redundancy, nfs and cassendra Check -----------------##
                if 'ngvs' in user_l:
                    status = ''
                    if 'fs.inp' in inp_name:
                        status = dbn(file_data, curr_date6, curr_date)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'db3.inp' in inp_name:
                        status = tape(file_data, pre_date1, month_date)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'fs.inp' in inp_name:
                        status = $status = zoo(file_data, curr_date, curr_date4)
                        parsed_hash[user][host][ip][inp_name] = status


        

            print("yes==============")
        else:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = issue1
            print("No==============")



    # print(inp_dir_path, user, inp_dir)
    print("==================","1")


def tape(data, date1, date2, inp_dir_path):
    """Used for backup.inp and fs_occ_backup.inp"""
    status = ""
    fail_reason = ""
    regex = '{}.*?voucherHistory'.format(month_date)
    if 'INFO:root:Filesystem backup ended at '+date1 in data:
        status = 'Success'
    elif 'Backup completed at '+date2 in data or 'Backup completed at '+curr_date7 in data:
        status = 'Success'
    elif len(re.findall(regex,data))>0:
        status = 'Success'
    else:
        status = 'Fail'
        fail_reason = 'BURA_BACKUP Failure'
    return status, fail_reason
    

def filesystem(data, date):
    """Used for fs.inp"""
    status = ""
    regex  = '{}.*?Backup completed'.format(curr_date6)
    if len(re.findall(regex, data))>0:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def dbn(data, date1, date2):
    """Used for db_backup.inp"""
    regex = "cfbackup.*?{}.*?log".format(curr_date2)
    status = ''
    if 'ScheduledBackup'+date1 in data:
        status = 'Success'
    elif 'INFO:root:Filesystem backup ended at '+date2 in data:
        status = 'Success'
    elif 'Recovery Manager complete' in data:
        status = 'Success'  
    elif 'HISTDG' in data or 'rman' in data:
        status = Success
    elif len(re.findall(regex, data))>0:
        status = 'Success'
    elif 'DUMP is complete' in data:
        status = 'Success'
    else:
        status = 'Fail'
    return status


if __name__ == '__main__':
    global users_details
    global parsed_hash


    month_date = str(datetime.today().strftime('%b %e'))
    pre_date1 = str(datetime.today().strftime('%Y_%m_%d -d -1 day'))
    curr_date = str(datetime.today().strftime('%Y-%m-%d'))
    curr_date2 = str(datetime.today().strftime('%Y%m%d'))
    curr_date4 = str(datetime.today().strftime('%y%m%d'))
    curr_date5 = str(datetime.today().strftime('%A, %B %d, %Y'))
    curr_date6 = str(datetime.today().strftime('%Y/%m/%d'))
    curr_date7 = str(datetime.today().strftime('%A, %B %e, %Y'))

    issue1 = 'Connectivity/Password Issue'
    parsed_hash = {}
    users_details = set_users_conf()
    read_opco_dir()
    print(parsed_hash)
