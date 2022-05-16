# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 13:19:31 2022

@author: wersc
"""

import pandas as pd 
import streamlit as st
import datetime as dt
st.set_page_config(layout="wide",initial_sidebar_state='collapsed')
import gspread
from dateutil import tz


def load_user_data(user):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    db = gc.open("Gym_Logger").worksheet(user).get_all_values()
    df = pd.DataFrame(db[1:],columns=db[0])

    return df

def update_sheet(user,old_data,new_data):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    worksheet = gc.open("Gym_Logger").worksheet(user)
    df = pd.concat([old_data,new_data],ignore_index=True).reset_index(drop=True)
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    return df

ref = load_user_data('Exercises').reset_index(drop=True)
exercise_data = {}
user = st.columns([1])[0]
ex_type,exercise,weight,reps = st.columns([1,2,1,1])
notes = st.columns([1])[0]

sidebar = st.sidebar
new_user = sidebar.text_input('New User',placeholder='Type Username Here')
if sidebar.button("Add New User"):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    col_names = ['User','Date','Time','MuscleGroup','Exercise','Weight','Reps','Notes','DateTime']
    gc.open("Gym_Logger").add_worksheet(title=new_user,rows=1,cols=len(col_names))
    gc.open("Gym_Logger").worksheet(new_user).update('A1:I1', [col_names])
    

sidebar.header('New Exercise')
new_ex = {}
new_ex['MuscleGroup'] = sidebar.text_input('Muscle Group',placeholder='Type Muscle Group Here')
new_ex['Exercise'] = sidebar.text_input('New Exercise',placeholder='Type Exercise Here')
new_ex['PP']  = 'TBA'
if sidebar.button("Add Exercise"):
    update_sheet('Exercises',ref,pd.DataFrame(new_ex,index = [0]))
  

worksheets = gspread.service_account_from_dict(st.secrets["gcp_service_account"]).open("Gym_Logger").worksheets()
users = sorted(ws.title for ws in worksheets if ws.title != 'Exercises' )
exercise_data['User'] = user.selectbox('User',users)
df = load_user_data(exercise_data['User'])
df[['Weight','Reps']] =  df[['Weight','Reps']].astype('float')


ex_type_value = ex_type.selectbox('Muscle Group',sorted(ref['MuscleGroup'].unique()))
body_ref = ref[ref['MuscleGroup'] == ex_type_value]
ex_selection = exercise.selectbox('Exercise Selection',sorted(body_ref['Exercise']))

exercise_data['MuscleGroup'] = ex_type_value
exercise_data['Exercise'] = ex_selection
exercise_data['Weight'] = weight.number_input('Weight',0.,1000.,50.0,5.)
exercise_data['Reps'] = reps.number_input('Reps',1,50,8,1)

curr_time = dt.datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('America/Denver'))

exercise_data['DateTime'] = str(curr_time)

exercise_data['Date']  = str(curr_time.date()) #date.date_input('Day',value = )
#exercise_data['Day'] = curr_time.strftime('%A')[:3]
exercise_data['Time'] = curr_time.time().strftime("%H:%M:%S")
exercise_data['Notes'] = notes.text_input('Notes',placeholder='Type Notes here')


#st.write(exercise_data)

submit, rest,_ = st.columns([1,3,5])

if submit.button('Submit'):
    df = update_sheet(exercise_data['User'],df,pd.DataFrame(exercise_data,index=[0]))

def done_with(df):
    if rest.button(f"Done with {exercise_data['Exercise']}"):
        exercise_data['Exercise'] = '---'
        exercise_data['Weight'] = 0
        df = update_sheet(exercise_data['User'],df,pd.DataFrame(exercise_data,index=[0]))


#done_with(df)


df['Volume'] = df['Weight']*df['Reps']

df = df[df['Exercise'] != '---']


gby = df.groupby(['Date','Exercise'])[['Weight','Reps','Volume','Time']].agg(['min','max','sum','count']).reset_index()
gby.columns = [f'{stat}{metric}' for metric, stat in gby.columns]

show_n = 5
st.header(f'Summary of last {show_n} exercises')

summary = pd.DataFrame()
summary['Date'] = gby['Date']
summary['FirstRepTime'] = gby['minTime']
summary['LastRepTime'] = gby['maxTime']
summary['Exercise'] = gby['Exercise']
summary['Weight'] = gby['minWeight'].astype(str) +" - "+ gby['maxWeight'].astype(str)
summary['Weight'] = summary['Weight'].apply(lambda x: x.split(" - ")[0] if x.split(" - ")[0]==x.split(" - ")[1] else x)
summary['Reps'] = gby['minReps'].astype(str) +" - "+ gby['maxReps'].astype(str)
summary['Reps'] = summary['Reps'].apply(lambda x: x.split(" - ")[0] if x.split(" - ")[0]==x.split(" - ")[1] else x)

summary['Sets'] = gby['countWeight']
summary['TotalReps'] = gby['sumReps'].astype(str)
summary['TotalVolume'] = gby['sumVolume'].astype(str)

#st.dataframe(df)
#st.dataframe(gby)
summary = summary.sort_values(['Date','LastRepTime']).drop(['FirstRepTime','LastRepTime'],axis=1)
st.write(summary.tail(show_n))

sidebar.markdown(
        """
Author: [JacWerCode](https://github.com/JacWerCode)
---
<a href="https://www.buymeacoffee.com/JacWerCode" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" 
width="180" height="50" ></a>
    """,  
    
        unsafe_allow_html=True,
    )