
# coding: utf-8

# In[1]:


import warnings
warnings.filterwarnings('ignore')
import sys
print('Python: {}'.format(sys.version))
#sys.path.append('/usr/local/bin/python2')
import os
os.getcwd()
import pandas as pd
print(pd.__version__)
import glob
import datetime
import time
import shutil
#from openpyxl import load_workbook
import openpyxl
from openpyxl import Workbook
from openpyxl.chart import (
    LineChart,
    Reference,
)
from openpyxl.chart.axis import DateAxis
import smtplib
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders


# In[2]:


#Config_File = glob.glob("C:\\Users\erairoy\\Desktop\\Automation\\MTN\\CONFIG\\CONFIG_PYTHON.xlsx")
Config_File = glob.glob("/home/southafrica/PM-Automation/MTN/CONFIG/CONFIG_PYTHON_UNIX.xlsx")
print('Configuration File:'+Config_File[0])
Configsheet_to_df_map = pd.read_excel(Config_File[0], sheet_name=None)
print('Configuration Loaded..')


# In[3]:


def InputFile_Exists(opco,df_Config,day_Y_M_D):
    try:
        
        Input_File_Path = df_Config[df_Config['CODENAME']=='INPUT_FILE_PATH']['CODEVALUE']
        Input_file = glob.glob(df_Config[df_Config['CODENAME']=='INPUT_FILE_PATH']['CODEVALUE'].iloc[0]+"MTN*"+day_Y_M_D+".xlsx")
        return Input_file[0]
    except IndexError:
        print('Input file missing in the directory:'+Input_File_Path)
        return "None"


# In[10]:


def Load_Format_Write(opco,Configsheet_to_df_map):
    #Load Input and Format Template Data
    df_Config = Configsheet_to_df_map[opco]
    
    today_Day = datetime.datetime.today().strftime("%d")
    Template_File_Path = df_Config[df_Config['CODENAME']=='OUTPUT_TEMPLATE_PATH']['CODEVALUE'].iloc[0]
    Template_File_Name = df_Config[df_Config['CODENAME']=='TEMPLATE_FILE_NAME']['CODEVALUE'].iloc[0]
    Template_File = glob.glob(Template_File_Path+Template_File_Name)
    #print(Input_file)
    #print(Template_File[0])
    #print(inputsheet_to_df_map['AIR'])
    template_to_df_map = pd.read_excel(Template_File[0], sheet_name="CCN")
    #print(template_to_df_map)
    
    day = datetime.datetime.today() 
    #today_M_D_Y = day.strftime("%m/%d/%Y")
    day_Y_M_D = day.strftime("%Y-%m-%d")
    #day_DD_MON = day.strftime("%d-%b")
    day_DD_MON_YYYY = day.strftime("%d-%b-%Y")

    ####
    Input_file = InputFile_Exists(opco,df_Config,day_Y_M_D)
    if Input_file != "None":
        inputsheet_to_df_map = pd.read_excel(Input_file, sheet_name=None,skiprows=6)
            
            #print(template_to_df_map['AIR'])
    else:
        print("No Input File is found")
        return
    
    for index,row in template_to_df_map.iterrows():
        try:
            template_to_df_map.loc[(template_to_df_map['IO2 IP']==row['IO2 IP']),['DBN backup(Daily)']]=inputsheet_to_df_map['CCN'][inputsheet_to_df_map['CCN']['Node-IP']==row['IO2 IP']].iloc[0]['DBN_BACKUP']
            template_to_df_map.loc[(template_to_df_map['IO2 IP']==row['IO2 IP'])&(template_to_df_map['DBN backup(Daily)']=='Done'),['DBN backup(Daily)']]=day_DD_MON_YYYY
        except IndexError:
            continue    
    Write_Normal_Output(df_Config,template_to_df_map,inputsheet_to_df_map,opco)


# In[9]:


def Write_Normal_Output(df_Config,template_to_df_map,inputsheet_to_df_map,opco):
    #Create Output File to Fill to fill data
    #import shutil
    Output_File_Path = df_Config[df_Config['CODENAME']=='OUTPUT_FILE_PATH']['CODEVALUE']
    Output_Temp_File_Path = df_Config[df_Config['CODENAME']=='OUTPUT_TEMPLATE_PATH']['CODEVALUE'].iloc[0]
    Output_File_Name = df_Config[df_Config['CODENAME']=='OUTPUT_FILE_NAME']['CODEVALUE'].iloc[0]
    Output_File = glob.glob(Output_Temp_File_Path+Output_File_Name)
    Output_File = shutil.copy2(Output_File[0], Output_File_Path.iloc[0]+"MTN-Backup_Tracker_OUT_"+str(datetime.date.today())+".xlsx") # complete target filename given
    CopyToFile = Output_File_Path.iloc[0]+"MTN-Backup_Tracker_OUT_"+str(datetime.date.today())+".xlsx"
    Output_File = Output_File_Path.iloc[0]+"MTN-Backup_Tracker_OUT_"+str(datetime.date.today())+".xlsx"
    print(Output_File)
    
    book = openpyxl.load_workbook(Output_File)
    writer = pd.ExcelWriter(Output_File, engine='openpyxl') 
    writer.book = book
    writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
    
    inputsheet_to_df_map['SDP'][['Node-Name','Node-IP','BURA_BACKUP','Fail Reason']].to_excel(writer, 'SDP(Daily)', index=False,startrow=1, header=False)
    inputsheet_to_df_map['AIR'][['Node-Name','Node-IP','BURA_BACKUP','Fail Reason']].to_excel(writer, 'AIR(Daily)', index=False,startrow=1, header=False)
    inputsheet_to_df_map['CCN'][['Node-Name','Node-IP','DBN_BACKUP','Fail Reason']].to_excel(writer, 'CCN(Daily)', index=False,startrow=1, header=False)
    inputsheet_to_df_map['SAPC'][['Node-Name','Node-IP','FSB','Fail Reason']].to_excel(writer, 'SAPC', index=False,startrow=1, header=False)
    #inputsheet_to_df_map['OCC'][['Node-Name','Node-IP','BURA_BACKUP','Fail Reason']].to_excel(writer, 'OCC', index=False,startrow=10, header=False)
    inputsheet_to_df_map['OCC']['Site']=inputsheet_to_df_map['OCC']['Node-Name']
    inputsheet_to_df_map['OCC'].loc[inputsheet_to_df_map['OCC']['Site'].str.contains("NDA"),['Site']]='Jo-burg'
    inputsheet_to_df_map['OCC'].loc[inputsheet_to_df_map['OCC']['Site'].str.contains("NLA"),['Site']]='Newlands'
    inputsheet_to_df_map['OCC'].loc[inputsheet_to_df_map['OCC']['Site'].str.contains("GEA"),['Site']]='Germiston'
    inputsheet_to_df_map['OCC'].loc[inputsheet_to_df_map['OCC']['Site'].str.contains("RNA"),['Site']]='Randburg'
    inputsheet_to_df_map['OCC'].sort_values(by=['Node-Name'])
    #inputsheet_to_df_map['OCC'][inputsheet_to_df_map['OCC']['Site'].contains("PG")]
    inputsheet_to_df_map['OCC'][['Node-Name','Site','Node-IP','BURA_BACKUP','Fail Reason']].to_excel(writer, 'vOCC', index=False,startrow=1, header=False)
    template_to_df_map[['Node Name','IO1 IP','IO2 IP','Date of Latest Backup','DBN backup(Daily)','Backup status IO backup(Quaterly)','Backup status FS backupp(Quaterly)','Remarks']].to_excel(writer, 'CCN', index=False,startrow=1, header=False)
    writer.save()
    
    Send_Email_SMTP(Output_File_Path.iloc[0],"MTN-Backup_Tracker_OUT_"+str(datetime.date.today())+".xlsx",opco,df_Config)


# In[6]:


def Send_Email_SMTP(Attachment_Path,Attachment_Name,opco,df_Config):
    subject = 'MTN Backup Tracker for '+ GetOpco_Name(opco)
    text = 'MTN Backup Tracker for '+ GetOpco_Name(opco)
    fromaddr = 'no-reply@AutoBOT'#df_Config[df_Config['CODENAME']=='EMAIL_TO_SEND']['CODEVALUE'].iloc[0]
    #toaddr = df_Config[df_Config['CODENAME']=='EMAIL_TO_SEND']['CODEVALUE'].iloc[0]
    COMMASPACE = ', '
    toaddr = ['gnoc.1st.la.mtn.rsaa@ericsson.com','PDLMTNFMIN@pdl.internal.ericsson.com','PDLFOINMTN@pdl.internal.ericsson.com','PDLHIFTMAN@pdl.internal.ericsson.com']#[df_Config[df_Config['CODENAME']=='EMAIL_TO_SEND']['CODEVALUE'].iloc[0],df_Config[df_Config['CODENAME']=='EMAIL_TO_SEND']['CODEVALUE1'].iloc[0]]


    msg = MIMEMultipart()

    msg['From'] = fromaddr
    msg['To'] = COMMASPACE.join(toaddr)
    msg['Subject'] = subject

    body = text

    msg.attach(MIMEText(body, 'plain'))

    filename = Attachment_Name
    #attachment = open('/home/congo/PM-Automation/MTN/ARCHIVE/IV/')#open("PATH OF THE FILE", "rb")

    part = MIMEBase('application', 'octet-stream')
    #part.set_payload((attachment).read())
    part.set_payload(open(Attachment_Path+Attachment_Name, "rb").read())

    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    msg.attach(part)
    text = msg.as_string()

    try:
       smtpObj = smtplib.SMTP('172.23.168.13',25)
       smtpObj.sendmail(fromaddr, toaddr, text)
       print("Successfully sent email")
    except smtplib.SMTPException:
       print("Error: unable to send email")


# In[7]:


def GetOpco_Name(opco):
    if opco =='NG':
        return 'Nigeria'
    elif opco == 'IV':
        return 'IvoryCoast'
    elif opco == 'SW':
        return 'Swaziland'
    elif opco == 'BIS':
        return 'Bissau'
    elif opco == 'CONG':
        return 'Congo'
    elif opco == 'BN':
        return 'Benin'
    elif opco == 'GH':
        return 'Ghana'
    elif opco == 'ZM':
        return 'Zambia'
    elif opco == 'SA':
        return 'SouthAfrica'


# In[8]:


if __name__ == '__main__':
    print(len(sys.argv))
    if len(sys.argv) < 2:
        print('To few arguments, please specify a filename')
    #filename = sys.argv[1]
    #print('Filename:', filename)
    #print(sys.argv[0])
    #print(sys.argv[2])
        
    for i,opco in Configsheet_to_df_map['OPCO'].iterrows():
        Load_Format_Write(opco.iloc[0],Configsheet_to_df_map)
        print(opco.iloc[0])

