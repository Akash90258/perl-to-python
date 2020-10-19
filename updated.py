import os
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
            print("yes==============")
        else:
            for array_ref1 in array_ref:
                parsed_hash[user][host][ip][array_ref1] = issue1


    print(parsed_hash)
    # print(inp_dir_path, user, inp_dir)
    print("==================")


if __name__ == '__main__':
    global users_details
    global parsed_hash
    curr_date2 = str(datetime.today().strftime('%Y%m%d'))

    issue1 = 'Connectivity/Password Issue'
    parsed_hash = {}
    users_details = set_users_conf()
    read_opco_dir()
