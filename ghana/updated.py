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
todays_datetime = datetime.datetime.today() - datetime.timedelta(2)

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

pre_date1 = ((datetime.datetime.today() - one_day_delta).strftime('%Y_%m_%d'))
pre_date2 = ((datetime.datetime.today() - one_day_delta).strftime('%Y/%m/%d'))
pre_date3 = ((datetime.datetime.today() - one_day_delta).strftime('%Y%m%d'))
pre_date4 = ((datetime.datetime.today() - one_day_delta).strftime('%Y-%m-%d'))

def load_config_ini():
    # Loading config.ini file into a dictionary
    config = ConfigParser()
    config.read('final_config.ini')
    config_data = dict(config.items('section1'))
    return config_data


def read_file(file_name):
    # Reading a file and returning its data
    # f = codecs.open(file_name, "r", encoding='utf-8')
    f = open(file_name, "r")
    file_data = f.read()#.encode('ascii', 'ignore').decode('utf-8',"")
    f.close()
    return file_data

def read_file_encoaded(file_name):
    # Reading a file and returning its data
    # f = codecs.open(file_name, "r", encoding='utf-8')
    f = open(file_name, "r")
    file_data = f.read()#.encode('ascii', 'ignore').decode('utf-8',"")
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


    ip, host = inp_dir.split("_")
    array_ref = users_details[user]
    user_l = user.lower().strip()

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
    else:
        nedate = read_file(inp_dir_path + "/nedate.inp")
        if curr_date2 in nedate:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = 'N/A'

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
                    if ('tape.inp' in inp_name or 'nfs.inp' in inp_name):
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = (status + "^^" + fail_reason)

                ##-- AIR Backup Check --##
                if 'air' == user_l:
                    status = ''
                    fail_reason = ''
                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name:
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason

                ##-- VS tape, nfs, ora, ora_archive  --##
                if 'ngvs' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'cassendra' in inp_name:
                        cassendra_flag += 1
                        for line in file_data.strip().split('\n'):
                            if month in line:
                                cassendra_arr.append(line.strip())
                        
                    if 'zoo.inp' in inp_name:
                        status = zoo(file_data, curr_date2)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name:
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = (status + "^^" + fail_reason)

                # -- OCC tape Check --##
                if 'occ' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name:
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason


                # ##-- CCN dbn Check --##
                if 'ccn' in user_l:
                    status = ''
                    if 'dbn.inp' in inp_name:
                        status = dbn(file_data, curr_date3, '')
                        parsed_hash[user][host][ip][inp_name] = status

                # ##-- EMA dbn Check --##
                if 'ema' in user_l:
                    status = ''
                    if 'proclog.inp' in inp_name:
                        status = proclog(file_data, month_date, curr_date2)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'sogconfig.inp' in inp_name:
                        status = sogconfig(file_data, curr_date4)
                        parsed_hash[user][host][ip][inp_name] = status



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
                parsed_hash[user][host][ip]['cassendra.inp'] = 'Fail'
        else:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = issue1


def tape(data, date1, date2, inp_dir_path):
    """Used for backup.inp and fs_occ_backup.inp"""
    status = ""
    fail_reason = ""
    regex1 = '(Backup completed at\W+{})'.format(date2)
    regex2 = '(Backup completed at\W+{})'.format(curr_date6)
    regex3 = '(INFO:root.*?Filesystem backup ended.*?at {})'.format(date1)

    if len(re.findall(regex3, data)) > 0:
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
        if 'air' in inp_dir_path:
            print(tape_data1,"==================",tape_data2)
        if ("there is no tape in drive" in tape_data2):
            fail_reason = "No Tape in Drive"
        else:
            if "status" in tape_data1[2]:
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


def dbn(data, date1, date2):
    """Used for db_backup.inp"""
    regex = "(rman_{}.*?Recovery Manager complete)".format(date2)
    status = ''
    if 'ScheduledBackup_' + date1 in data:
        status = 'Success'
    elif len(re.findall(regex, data)) > 0 or "Recovery Manager complete" in data:
        status = 'Success'
    elif 'DUMP is complete' in data:
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

def zoo(data, date):
    status = ''
    if "backup_zk_"+date in data or "TCZookeeperbackup_"+date in data or "YoZookeeperbackup_" + date in data:
        status = 'Success'
    else:
        status = 'Fail'
    return status



def main():
    global users_details
    global parsed_hash
    global config_data
    parsed_hash = {}
    config_data = load_config_ini()
    users_details = set_users_conf()
    read_opco_dir()
    return parsed_hash


if __name__ == '__main__':
    parsed_hash = main()
    print("========================================")
    print(parsed_hash)
