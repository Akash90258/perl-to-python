import os
import re
from datetime import datetime

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0


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
    return file_data  # .encode('utf-8')


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
        # break


def read_users_dir(user_dir, user):
    hosts = []
    if os.path.isdir(user_dir):
        hosts = os.listdir(user_dir)
    else:
        print("Can't open the current directory")
    for inp_dir in hosts:
        # $inp_dir_hash->{$user}->{$inp_dir} = 1; TODO : not getting this line
        inp_dir_path = user_dir + "/" + inp_dir
        # if user not in inp_dir_hash:
        #     inp_dir_hash[user] = {}
        #     inp_dir_hash[user][inp_dir] = 1;
        # else:
        #     inp_dir_hash[user][inp_dir] = 1;
        read_inp(inp_dir_path, user, inp_dir)
    # print(inp_dir_hash)
    # print(inp_dir_path)
    # print("============================")


def read_inp(inp_dir_path, user, inp_dir):
    sdp_geo_check = 0
    sdp_geo = ''
    cassendra_arr = []
    cassandra_flag = 0

    ip, host = inp_dir.split("_")
    array_ref = users_details[user]

    user_l = user.lower().strip()

    # see in pma_bkup_tracker file for geo-redundancy
    array_ref_geo = []
    if ('sdp' in user_l or  'vs' in user_l) :
        array_ref_geo = users_details[user+"-geo-red"];
        if user+"-geo-red" not in parsed_hash:
            parsed_hash[user+"-geo-red"] = {}
        if host not in parsed_hash[user+"-geo-red"]:
            parsed_hash[user+"-geo-red"][host] = {}
        if ip not in parsed_hash[user+"-geo-red"][host]:
            parsed_hash[user+"-geo-red"][host][ip] = {}


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
        # parsed_hash[user+"-geo-red"] = {}
    if host not in parsed_hash[user]:
        parsed_hash[user][host] = {}
        # parsed_hash[user+"-geo-red"][host] = {}
    if ip not in parsed_hash[user][host]:
        parsed_hash[user][host][ip] = {}
        # parsed_hash[user+"-geo-red"][host][ip] = {}

    if len(inp_files2) == 0:
        for array_ref1 in array_ref:
            parsed_hash[user][host][ip][array_ref1] = issue1

        for array_ref_geo1 in array_ref_geo:
            parsed_hash[user+"-geo-red"][host][ip][array_ref_geo1] = issue1


    else:
        nedate = read_file(inp_dir_path + "/nedate.inp")
        if curr_date2 in nedate:
        # if '20201102' in nedate:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = 'N/A'

            for array_ref_geo1 in array_ref_geo:
                parsed_hash[user+"-geo-red"][host][ip][array_ref_geo1] = 'N/A'

            for inp_name in inp_files:
                inp_name = inp_name.strip()
                inp_file = "{}/{}".format(inp_dir_path, inp_name)
                file_data = read_file(inp_file)

                ##-- AIR Backup Check --##
                if 'air' == user_l:
                    status = ''
                    fail_reason = ''
                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name:
                        status, fail_reason = tape(
                            file_data, curr_date, curr_date5, inp_dir_path
                        )
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason

                #-- OCC tape Check --##
                if 'occ' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name:
                        status, fail_reason = tape(file_data, curr_date, curr_date5, inp_dir_path)
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason

                ##-- SDP geo-redundancy and tape Check --##
                if 'sdp' in user_l:
                    status = ''
                    fail_reason = ''
                    # regex = "{}\s+\d+\:\d+\:\d+\s+Standby\s+database\s+replication\s+OK".format(curr_date)
                    regex = "({}\s+\d+\:\d+\:\d+\s+Standby\s+database\s+replication\s+OK)".format(curr_date)
                    if 'TTMonitor.inp' in inp_name or 'TTMonitorlog.inp' in inp_name:
                        sdp_geo_check += 1
                        geo_str = file_data.split('\n')
                        arr_len = len(geo_str)
                        if arr_len > 4:
                            parsed_hash[user+"-geo-red"][host][ip]['geo-redundancy.inp'] = 'Fail'

                    if 'TTMonitorStandby.inp' in inp_name and parsed_hash[user+"-geo-red"][host][ip]['geo-redundancy.inp'] == 'N/A':
                        if len(re.findall(regex, file_data)) > 0:
                            parsed_hash[user+"-geo-red"][host][ip]['geo-redundancy.inp'] = 'Success'
                        else:
                            parsed_hash[user+"-geo-red"][host][ip]['geo-redundancy.inp'] = 'Fail'

                
                    if 'tape.inp' in inp_name or 'nfs.inp' in inp_name or 'tape_nfs.inp' in inp_name:
                        status, fail_reason = tape(file_data, curr_date, curr_date5, inp_dir_path)
                        parsed_hash[user][host][ip][inp_name] = status + "^^" + fail_reason

                ##-- NGVS geo-redundancy, nfs and cassendra Check --##
                if 'ngcrs' in user_l:
                    status = ''
                    if 'appfs.inp' in inp_name:
                        status = appfs(file_data, pre_date3)
                        # status = dbn(file_data, curr_date6, curr_date)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'appfs1.inp' in inp_name:
                        status = cdr(file_data, pre_date3);
                        # status = tape(file_data, pre_date1, month_date, inp_dir_path)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'maintenance.inp' in inp_name:
                        status = oradb(file_data, pre_date4);
                        # status = zoo(file_data, curr_date, curr_date4)
                        parsed_hash[user][host][ip][inp_name] = status

                # ##-- CCN dbn Check --##
                if 'ccn' in user_l:
                    status = ''
                    if 'dbn.inp' in inp_name:
                        status = dbn(file_data, curr_date3, '')
                        parsed_hash[user][host][ip][inp_name] = status

                ##-- MINSAT fs and db Check --##
                if 'minsat' in user_l:
                    status = ''
                    fail_reason = ''

                    if 'fs.inp' in inp_name:
                        status = filesystem(file_data, curr_date6)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'db.inp' in inp_name:
                        status = dbn(file_data, pre_date1, '')
                        parsed_hash[user][host][ip][inp_name] = status

                ##-- VS tape, nfs, ora, ora_archive and geo-redundancy Check --##
                if 'vs' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'ora.inp' in inp_name and 'ora_archive.inp' in inp_name:
                        status = ora(file_data, curr_date2)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'tape.inp' in inp_name and 'nfs.inp' in inp_name:
                        status, fail_reason = tape(file_data, curr_date, curr_date5, inp_dir_path)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'cassendra' in inp_name:
                        cassandra_flag += 1
                        date_str = file_data.split('\n')
                        for row in date_str:
                            if 'month' in row:
                                cassendra_arr.append(ow.strip())

                ##--EMA proclog and sogconfig Check --##
                if 'ema' in user_l:
                    status = ''
                    fail_reason = ''

                    if 'proclog.inp' in inp_name:
                        status = proclog(file_data, month_date, curr_date2)
                        parsed_hash[user][host][ip][inp_name] = status

                    if 'sogconfig.inp' in inp_name:
                        status = sogconfig(file_data, curr_date4)
                        parsed_hash[user][host][ip][inp_name] = status


                ##-- CRS appfs, archived CDR and oracle database Check,fs backup --##
                if 'crs' in user_l:
                    status = ''
                    fail_reason = ''
                    if 'db.inp' in inp_name:
                        status = dbn(file_data, pre_date1, pre_date3)
                        parsed_hash[user][host][ip][inp_name] = status


            #-- geo-redundancy check --##
            if sdp_geo_check == 2 and parsed_hash[user+"-geo-red"][host][ip]['geo-redundancy.inp'] == 'N/A':
                parsed_hash[user+"-geo-red"][host][ip]['geo-redundancy.inp'] = 'Success'
        else:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = issue1
            for array_ref_geo1 in array_ref_geo:
                parsed_hash[user+"-geo-red"][host][ip][array_ref_geo1] = issue1
    
    # print(parsed_hash)                
    # print(inp_dir_path, user, inp_dir)


def tape(data, date1, date2, inp_dir_path):
    """Used for backup.inp and fs_occ_backup.inp"""
    status = ""
    fail_reason = ""
    regex1 = '(Backup\s+completed\s+at\W+{})'.format(date2)
    regex2 = '(Backup\s+completed\s+at\W+{})'.format(curr_date7)
    if 'INFO:root:Filesystem backup ended at ' + date1 in data:
        status = 'Success'
    elif len(re.findall(regex1, data)) > 0 or len(re.findall(regex2, data)) > 0:
        status = 'Success'
    else:
        status = 'Fail'
        tape_data1 = ''
        tape_data2 = ''
        if os.path.exists(inp_dir_path+"/tape2.inp"):
            tape_data1  = read_file(inp_dir_path+"/tape2.inp")
        if os.path.exists(inp_dir_path+"/tape1.inp"):
            tape_data2  = read_file(inp_dir_path+"/tape1.inp")

        tape_data1 = tape_data1.split('\n')
        if ("there is no tape in drive"):
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
    regex = "(rman\_{}.*?Recovery\s+Manager\s+complete)".format(curr_date2)
    status = ''
    if 'ScheduledBackup_' + date1 in data:
        status = 'Success'
    elif len(re.findall(regex, data)) > 0:
        status = 'Success'
    elif 'DUMP is complete' in data:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def zoo(data, date, date2):
    status = ''
    if 'backup_zk_{}'.format(date):
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
    regex = '(sogadm\s+sog.*?{}\s+{}.*?{})'.format(month, day1, date)
    regex1 = "(sogadm\s+sog.*?{}\s+{}.*?{})".format(month, day2, date)
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


def appfs(data, date):
    status = ''
    regex = 'root_backup(.*?){}'.format(date)
    if len(re.findall(regex, data)):
        status = 'Success'
    else:
        status = 'Fail'
    return status

def cdr(data, date):
    status = ''
    if 'swezdesma_{}'.format(date) in data:
        status = 'Success'
    else:
        status = 'Fail'
    return status


def oradb(data, date):
    status = ''
    if 'rman_bkup_{}'.format(date) in data:
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


sdp_geo_check = 0
cassandra_flag = 0
sdp_geo = ''
cassendra_arr = []
month_date = str(datetime.today().strftime('%b %e'))
pre_date1 = str(datetime.today().strftime('%Y_%m_%d -d -1 day'))
curr_date = str(datetime.today().strftime('%Y-%m-%d'))
curr_date2 = str(datetime.today().strftime('%Y%m%d'))
curr_date3 = str(datetime.today().strftime('%Y_%m_%d'))
curr_date4 = str(datetime.today().strftime('%y%m%d'))
curr_date5 = str(datetime.today().strftime('%A, %B %d, %Y'))
curr_date6 = str(datetime.today().strftime('%Y/%m/%d'))
curr_date7 = str(datetime.today().strftime('%A, %B %e, %Y'))
pre_date1 = str(datetime.today().strftime('%Y_%m_%d'))
pre_date2 = str(datetime.today().strftime('%Y/%m/%d'))
pre_date3 = str(datetime.today().strftime('%Y%m%d'))
pre_date4 = str(datetime.today().strftime('%Y-%m-%d'))

issue1 = 'Connectivity/Password Issue'

if __name__ == '__main__':
    global users_details
    global parsed_hash
    global config_data
    config_data = load_config_ini()
    sdp_geo_check = 0
    sdp_geo = ''
    cassandra_flag = 0
    cassendra_arr = []
    inp_dir_hash = {}
    day1 = str(datetime.today().strftime('%d'))
    day2 = str(datetime.today().strftime('%e'))
    month = str(datetime.today().strftime('%b'))
    month_date = str(datetime.today().strftime('%b %e'))
    pre_date1 = str(datetime.today().strftime('%Y_%m_%d -d -1 day'))
    curr_date = str(datetime.today().strftime('%Y-%m-%d'))
    curr_date2 = str(datetime.today().strftime('%Y%m%d'))
    curr_date3 = str(datetime.today().strftime('%Y_%m_%d'))
    curr_date4 = str(datetime.today().strftime('%y%m%d'))
    curr_date5 = str(datetime.today().strftime('%A, %B %d, %Y'))
    curr_date6 = str(datetime.today().strftime('%Y/%m/%d'))
    curr_date7 = str(datetime.today().strftime('%A, %B %e, %Y'))


    pre_date1 = str(datetime.today().strftime('%Y_%m_%d'))
    pre_date2 = str(datetime.today().strftime('%Y/%m/%d'))
    pre_date3 = str(datetime.today().strftime('%Y%m%d'))
    pre_date4 = str(datetime.today().strftime('%Y-%m-%d'))


    issue1 = 'Connectivity/Password Issue'
    parsed_hash = {}
    users_details = set_users_conf()
    read_opco_dir()
    print("========================================")
    print(parsed_hash)
