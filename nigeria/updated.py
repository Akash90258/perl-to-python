import datetime
import os
import re
import codecs
from ConfigParser import ConfigParser

sdp_geo = ''
sdp_geo_check = 0
cassendra_flag = 0
cassendra_arr = []
issue1 = 'Connectivity/Password Issue'

one_day_delta = datetime.timedelta(1)
todays_datetime = datetime.datetime.today() - datetime.timedelta(7)

day1 = str(todays_datetime.strftime('%d'))
day2 = str(todays_datetime.strftime('%e'))
month = str(todays_datetime.strftime('%b'))
month_date = str(todays_datetime.strftime('%b %e'))
curr_date = str(todays_datetime.strftime('%Y-%m-%d'))
curr_date2 = str(todays_datetime.strftime('%Y%m%d'))
curr_date3 = str(todays_datetime.strftime('%Y_%m_%d'))
curr_date4 = str(todays_datetime.strftime('%y%m%d'))
curr_date5 = str(todays_datetime.strftime('%A, %B %d, %Y'))
curr_date6 = str(todays_datetime.strftime('%Y/%m/%d'))
curr_date7 = str(todays_datetime.strftime('%A, %B %e, %Y'))

pre_date1 = ((todays_datetime - one_day_delta).strftime('%Y_%m_%d'))
pre_date2 = ((todays_datetime - one_day_delta).strftime('%Y/%m/%d'))
pre_date3 = ((todays_datetime - one_day_delta).strftime('%Y%m%d'))
pre_date4 = ((todays_datetime - one_day_delta).strftime('%Y-%m-%d'))

def load_config_ini():
    # Loading config.ini file into a dictionary
    config = ConfigParser()
    config.read('final_config.ini')
    config_data = dict(config.items('section1'))
    return config_data


def read_file(file_name):
    # Reading a file and returning its data
    f = open(file_name, "r")
    file_data = f.read()
    f.close()
    return file_data

def read_file_encoaded(file_name):
    # Reading a file and returning its data
    f = open(file_name, "r")
    file_data = f.read()
    f.close()
    return repr(file_data)


def set_users_conf():
    # Read pma_bkp_tracker.conf file and create dict.
    users_details = {}
    conf_file = config_data['pma_bkup_tracker']
    fh = open(conf_file, "r")
    data = fh.readlines()
    fh.close()
    for line in data:
        line = line.strip()
        key, values = line.split("=")
        users_details[key.strip()] = values.split(',')
    return users_details


def read_opco_dir():
    # Reading All node type directories from datasrc folder
    basedir = config_data['base_dir_inp_files']
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
        inp_dir_path = user_dir + "/" + inp_dir
        if os.path.isdir(inp_dir_path):
            read_inp(inp_dir_path, user, inp_dir)


def read_inp(inp_dir_path, user, inp_dir):
    sdp_geo_check = 0
    sdp_geo = ''
    cassendra_arr = []
    cassendra_flag = 0

    # when last character is alphabet like a or b
    if 'sdp' in user.lower().strip():
        if inp_dir[-1] == 'b' :
            inp_dir = inp_dir[0:-1]+'a'
        if inp_dir[-1] == '2' :
            inp_dir = inp_dir[0:-1]+'1'


    ip, host = inp_dir.split("_")
    array_ref = users_details[user]

    user_l = user.lower().strip()
    array_ref_geo = []
    if ('sdp' in user_l or 'ngvs' in user_l):
        array_ref_geo = users_details[user + "-geo-red"];
        if user + "-geo-red" not in parsed_hash:
            parsed_hash[user + "-geo-red"] = {}
        if host not in parsed_hash[user + "-geo-red"]:
            parsed_hash[user + "-geo-red"][host] = {}
        if ip not in parsed_hash[user + "-geo-red"][host]:
            parsed_hash[user + "-geo-red"][host][ip] = {}

    inp_files = []
    if os.path.isdir(inp_dir_path):
        inp_files = os.listdir(inp_dir_path)
    else:
        print("Can't open the current directory")

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
        for array_ref_geo1 in array_ref_geo:
            parsed_hash[user + "-geo-red"][host][ip][array_ref_geo1] = issue1
    else:
        nedate = read_file(inp_dir_path + "/nedate.inp")
        if curr_date2 in nedate:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = 'N/A'
            for array_ref_geo1 in array_ref_geo:
                parsed_hash[user + "-geo-red"][host][ip][array_ref_geo1] = 'N/A'

            for inp_name in inp_files:
                inp_name = inp_name.strip()
                inp_file = "{}/{}".format(inp_dir_path, inp_name)
                if os.path.isdir(inp_file):
                    continue
                file_data = read_file(inp_file)

                ##-- SDP geo-redundancy and tape Check --##
                if 'sdp' in user_l:
                    status = ''
                    fail_reason = ''
                    if ('tape.inp' in inp_name):
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = (status + "^^" + fail_reason)

                    if 'TTMonitor.inp' in inp_name or 'TTMonitorlog.inp' in inp_name:
                        # print("--------i am in ")
                        sdp_geo_check += 1
                        geo_str = file_data.strip().split('\n')
                        arr_len = len(geo_str)
                        # print(geo_str)
                        # print(arr_len,"===================")
                        if arr_len > 5:
                            parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] = 'Fail'
                        else:
                            parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] = 'Success'

                    # regex = "({}.*?Standby database replication OK)".format(curr_date)
                    # if 'TTMonitorStandby.inp' in inp_name and parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] == 'N/A':
                    #     # print("///////////////////////////////////////////",regex)
                    #     if len(re.findall(regex, file_data)) > 0:
                    #         # print("//////////////////////////-------------")
                    #         parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] = 'Success'
                    #     else:
                    #         # print("//////////////////////////-------------===============")
                    #         parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] = 'Fail'


                ##-- AIR Backup Check --##
                if 'air' == user_l:
                    status = ''
                    fail_reason = ''
                    if ('tape.inp' in inp_name):
                        try:
                            temp_value = pre_day_hash[user_l][host.lower()][ip]['tape']
                            # print("--------///////////",temp_value, pre_date4, pre_date3)
                            flag  = 1
                        except:
                            # print("----------------------temp_value")
                            flag = 0
                        if flag:
                            status, fail_reason = tape(file_data, pre_date4, pre_date3, inp_dir_path)
                        else:
                            status, fail_reason = tape(file_data, curr_date, curr_date5, inp_dir_path)
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason

                
                # ##-- CCN dbn Check --##
                if 'ccn' in user_l:
                    status = ''
                    if 'dbn.inp' in inp_name:
                        status = dbn(file_data, pre_date1, '')
                        parsed_hash[user][host][ip][inp_name] = status


                # -- OCC tape Check --##
                if 'occ' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'tape.inp' in inp_name:
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason


                ##-- VS tape, nfs, ora, ora_archive  --##
                if 'vccn' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'Vccn_config_backup.inp' in inp_name:
                        status = Vccn_config_backup(file_data, pre_date4)
                        parsed_hash[user][host][ip][inp_name] = status


                ##-- ngvs tape, cassendra  --##
                if 'ngvs' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'cassendra' in inp_name:
                        cassendra_flag += 1
                        for line in file_data.strip().split('\n'):
                            if month in line:
                                cassendra_arr.append(line.strip())
                    
                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name:
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = (status + "^^" + fail_reason)

                    if 'geo.inp' in inp_name:
                        status = ngvs_geo(file_data)
                        parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] = status


            ##------------- cassendra check -------------##
            flag = 0
            for date_val in cassendra_arr:
                if month+" "+day1 in date_val or month+" "+day2 in date_val:
                    flag = 1

            if cassendra_flag > 0 :
                if flag:
                    parsed_hash[user][host][ip]['cassendra.inp'] = 'Success'
                else:
                    parsed_hash[user][host][ip]['cassendra.inp'] = 'Fail'

            if 'cassendra.inp' in array_ref and cassendra_flag == 0:
                parsed_hash[user][host][ip]['cassendra.inp'] = 'N/A'

            # --------------------
            # try:
            #     print(parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'],"==========",sdp_geo_check)
            # except:
            #     pass
            if sdp_geo_check == 2 and parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] == 'N/A':
                parsed_hash[user + "-geo-red"][host][ip]['geo-redundancy.inp'] = 'Success'
        else:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = issue1

            for array_ref_geo1 in array_ref_geo:
                parsed_hash[user + "-geo-red"][host][ip][array_ref_geo1] = issue1


def tape(data, date1, date2, inp_dir_path):
    """Used for backup.inp and fs_occ_backup.inp"""
    status = ""
    fail_reason = ""
    regex1 = '(Backup\s+completed\s+at\W+{})'.format(date2)
    regex2 = '(Backup\s+completed\s+at\W+{})'.format(curr_date6)
    regex3 = '(INFO:root.*?Filesystem.*backup started.*?at {})'.format(curr_date)

    regex4 = '(Filesystem.*backup.*ended.*?at {})'.format(date1)
    # print(regex4, inp_dir_path)
    if len(re.findall(regex4, data)) > 0:
        status = 'Success'
    elif len(re.findall(regex1, data)) > 0 or len(re.findall(regex2, data)) > 0:
        status = 'Success'
    else:
        status = 'Fail'
        tape_data1 = ''
        tape_data2 = ''
        if os.path.exists(inp_dir_path + "/tape2.inp"):
            tape_data1 = read_file(inp_dir_path + "/tape2.inp")
        if os.path.exists(inp_dir_path + "/tape1.inp"):
            tape_data2 = read_file(inp_dir_path + "/tape1.inp")
        tape_data1 = tape_data1.split('\n')
        # if 'air' in inp_dir_path:
        #     print(tape_data1,"==================",tape_data2, inp_dir_path)
        if ("there is no tape in drive" in tape_data2):
            fail_reason = "No Tape in Drive"
        else:
            if len(tape_data1) > 3 and "status" in tape_data1[2]:
                fail_reason = tape_data1[2]
    return status, fail_reason


def filesystem(data, date):
    """Used for fs.inp"""
    status = ""
    regex = '{}.*?Backup completed'.format(curr_date6)
    if len(re.findall(regex, data)) > 0:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def fs_backup(data):
    """Used for fs.inp"""
    status = ""
    fsb = data.split('\n')
    fsbk = fsb[2]
    regex = "(Backup_*?{})".format(curr_date)
    if len(re.findall(regex, data)) > 0:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def dbn(data, date1, date2):
    """Used for db_backup.inp"""
    status = ''
    if 'ScheduledBackup_' + date1 in data:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def ora(data, date):
    status = ''
    regex = "(This backup\W+{}.*?session is completed and finished)".format(date)
    if len(re.findall(regex, data)):
        status = 'Success'
    else:
        status = 'Fail'
    return status


def proclog(data, mdate, date):
    status = ''
    regex = '(sogadm sog.*?{}.*?{}.*?{})'.format(month, day1, date)
    regex1 = '(sogadm sog.*?{}.*?{}.*?{})'.format(month, day2, date)
    if len(re.findall(regex, data)) > 0 or len(re.findall(regex1, data)) > 0:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def sogconfig(data, date):
    status = ''
    regex = '(sogconfig_backup.{})'.format(date)
    if len(re.findall(regex, data)):
        status = 'Success'
    else:
        status = 'Fail'
    return status

def Vccn_config_backup(data, date):
    status = ''
    regex = '(sogconfig_backup.{})'.format(date)
    if "BACKUP_{}".format(date) in data:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def zoo(data, date):
    status = ''
    if ("backup_zk_"+date in data or
        "TCZookeeperbackup_"+date in data or
        "YoZookeeperbackup_" + date in data):
        status = 'Success'
    else:
        status = 'Fail'
    return status

def ngvs_geo(data):
    status = ''
    geo_str = data.split('Datacenter')
    un_count1 = 0
    un_count2 = 0
    geo_str_temp = geo_str[1].split('\n')
    for string in geo_str_temp:
        if 'UN' in string:
            un_count1 += 1
    geo_str_temp = geo_str[2].split('\n')
    for string in geo_str_temp:
        if 'UN' in string:
            un_count2 += 1
    if 'DC1' in geo_str[1] and 'DC2' in geo_str[2]:
        if un_count1 == 15 and un_count2 == 15 :
            status = 'Success'
        else:
            status = 'Fail'
    return status

def pre_day_hash_dict():
    hash_dict = {
        "air" : {
            'asair8' : {
                '10.226.8.27' : {
                    'tape' : 1
                }
            },
            'asair8' : {
                '10.197.8.225' : {
                    'tape' : 1
                }
            },
            'asair7' : {
                '10.226.8.25' : {
                    'tape' : 1
                }
            },
            'asair6' : {
                '10.226.8.157' : {
                    'tape' : 1
                },
                '10.197.88.27' : {
                    'tape' : 1
                }
            },
            'asair11' : {
                '10.226.8.62' : {
                    'tape' : 1
                }
            },
            'apair5' : {
                '10.197.8.158' : {
                    'tape' : 1
                }
            }
        },
        "ecms" : {
            'ibcmsa1' : {
                '10.198.37.33' : {
                    'tape' : 1
                }
            },
            'ibcmsa2' : {
                '10.198.37.35' : {
                    'tape' : 1
                }
            }
        }
    }
    return hash_dict

def main():
    global users_details
    global parsed_hash
    global config_data
    global pre_day_hash
    parsed_hash = {}
    pre_day_hash = pre_day_hash_dict()
    config_data = load_config_ini()
    users_details = set_users_conf()
    read_opco_dir()
    return parsed_hash


if __name__ == '__main__':
    parsed_hash = main()
    print("========================================")
    print(parsed_hash["sdp-geo-red"])
