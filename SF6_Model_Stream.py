import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from simple_salesforce import Salesforce
import collections
import os
import time
import sys 
import streamlit as st
import altair as alt

DATASOURCE_SQL = st.secrets["DataSource_SQL"]
PASSWORD_SQL = st.secrets["Password_SQL"]
USERID_SQL = st.secrets["UserID_SQL"]

USER_SALES = st.secrets['sf_user']
PASSWORD = st.secrets['sf_pass']
TOKEN = st.secrets['sf_token']
USER_SPLUNK = st.secrets["sp_user"]

sf = Salesforce(username=USER_SALES,
                password=PASSWORD,
                security_token=TOKEN)

def get_pcsn_info(pcsn_list):
    records=[]
    query = sf.query(f"""
                    SELECT Name,Account_Name__c,Service_Territory__r.Country,
                    Service_Territory__r.Description,Billing_Type__c,Primary_Service_Resource__r.Resource_Email__c FROM Asset
                    WHERE Name IN {pcsn_list}
                """)
    [records.append(x) for x in query.get('records')]
    return records

def make_df_results(records):
    entries=[]
    for record in records:
        entry=collections.OrderedDict()
        try:
            entry['SN'] = record.get('Name')
            entry['Account'] = record.get('Account_Name__c')
            territorio = record.get('Service_Territory__r')
            if territorio:
                entry['Country'] = territorio.get('Country')
                entry['Description'] = territorio.get('Description')
            mail = record.get('Primary_Service_Resource__r')
            if mail:
                entry['mail']=mail.get('Resource_Email__c')
                
            entry['Billing Type']=record.get('Billing_Type__c')
            
            entries.append(entry)
        except:
            print(f"Problems retrieving data for {record.get('name')}")
            entries.append(entry)
            continue
    return entries


df = pd.read_csv("C:/projects/Models Azure/SF6/Streamlit/SF6_Slope.csv")
df.Slope=df.Slope*-1

df_Data = pd.read_csv("C:/VMSOS/Data/SF6/SF6_Data.csv")

st.write(""" 
# SF6 Model Working
""")

Slope = st.slider("Pick the Slope",min_value=0.01,max_value=0.5,step=0.01)

if Slope == 0.01:
    Slope = 0.3

st.write(""" 
### PCSN´s detected with an Slope bigger than """,Slope)
Serial_to_analisys = df[df['Slope']>Slope]

test = Serial_to_analisys['PCSN'].astype(str)

Serial_number = ['H19'+sn for sn in test]
records = get_pcsn_info(tuple(Serial_number))
results = make_df_results(records)
df_CSR = pd.DataFrame(results)

st.write(""" 
## Contact. (Expand if needed)
""")

st.dataframe(df_CSR)

for PCSN_number in test:
    
    df_print= df_Data[df_Data.PCSN==int(PCSN_number)]

    x = df_print.TimeStamp
    a = df_print.Avg
    if len(a)>1:

        fig, ax = plt.subplots()
        ax.plot(x,a, label='SF6 Pressure')
    
        plt.xlabel('Date', fontsize=20)
        plt.ylabel('SF6 Pressure ', fontsize=20)
        plt.title('H19{} SF6 Pressure '.format(PCSN_number), fontsize=25)
        ax.legend(fontsize=14)
        ax.grid()

        st.pyplot(fig)




Serial_number = ['H19'+sn for sn in test]
st.write(Serial_number)
