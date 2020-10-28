try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

# instantiate
config = ConfigParser()

# parse existing file
config.read('final_config.ini')
config_data = dict(config.items('section1'))
print(config_data)














# try:
#     from configparser import ConfigParser
# except ImportError:
#     from ConfigParser import ConfigParser  # ver. < 3.0

# # instantiate
# config = ConfigParser()

# # parse existing file
# config.read('final_config.ini')

# # read values from a section
# # string_val = config.get('3_nodeip', 'string_val')
# # bool_val = config.getboolean('section_a', 'bool_val')
# # int_val = config.getint('section_a', 'int_val')
# # float_val = config.getfloat('section_a', 'pi_val')



# # print(string_val)
# # print(bool_val)
# # print(int_val)
# # print(float_val)



# # # add a new section and some values
# # config.add_section('section_b')
# # config.set('section_b', 'meal_val', 'spam')
# # config.set('section_b', 'not_found_val', '404')



# data = dict(config.items('section1'))
# # for key, value in data.items():
# # 	data[key] = value.split(',')
# print(data)
# 	# print(key, value)
# 	# print("-----------------------")