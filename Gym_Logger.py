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


@st.cache
def load_exercises():    
    return  pd.read_csv('NS_Ref.csv').set_index('Exercise')

def load_user_data(user):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    db = gc.open("Gym_Logger").worksheet(user).get_all_values()
    df = pd.DataFrame(db[1:],columns=db[0])
    df[['Weight','Reps']] =  df[['Weight','Reps']].astype('float')
    return df

def update_sheet(user,df):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    worksheet = gc.open("Gym_Logger").worksheet(user)
    submitted_ex = pd.DataFrame(exercise_data,index=[0]) 
    df = pd.concat([df,submitted_ex],ignore_index=True).reset_index(drop=True)
    #st.write(df.columns.values.tolist())
    #st.write(df.values.tolist())
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())
    return df

ref = load_exercises().reset_index()
exercise_data = {}
user = st.columns([1])[0]
ex_type,exercise,weight,reps = st.columns([1,2,1,1])
notes = st.columns([1])[0]

sidebar = st.sidebar
sidebar.header('New User')
new_user = sidebar.text_input('New User',placeholder='Type Username Here')
if sidebar.button("Add New User"):
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    col_names = ['User','Date','Time','MuscleGroup','Exercise','Weight','Reps','Notes','DateTime']
    gc.open("Gym_Logger").add_worksheet(title=new_user,rows=1,cols=len(col_names))
    gc.open("Gym_Logger").worksheet(new_user).update('A1:I1', [col_names])
    
def add_new():
    sidebar.header('New Exercise')
    muscle_group = sidebar.text_input('Muscle Group',placeholder='Type Muscle Group Here')
    new_exercise = sidebar.text_input('New Exercise',placeholder='Type Exercise Here')
    #push_pull = sidebar.select_box('Push/Pull',placeholder='Push or Pull')
    if sidebar.button("Add Exercise"):
        pass
  

    

worksheets = gspread.service_account(filename='cashsheets2.json').open("Gym_Logger").worksheets()
users = sorted(ws.title for ws in worksheets)
exercise_data['User'] = user.selectbox('User',users)
df = load_user_data(exercise_data['User'])

ex_type_value = ex_type.selectbox('Muscle Group',sorted(ref['Body'].unique()))
body_ref = ref[ref['Body'] == ex_type_value]
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
    df = update_sheet(exercise_data['User'],df)

if rest.button(f"Done with {exercise_data['Exercise']}"):
    exercise_data['Exercise'] = '---'
    exercise_data['Weight'] = 0

    df = update_sheet(exercise_data['User'],df)

df['Volume'] = df['Weight']*df['Reps']


df = df[df['Exercise'] != '---']


gby = df.groupby(['Date','Exercise'])[['Weight','Reps','Volume','Time']].agg(['min','max','sum','count']).reset_index()
gby.columns = [f'{stat}{metric}' for metric, stat in gby.columns]

show_n = 5
st.header(f'Last {show_n} exercises')

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
summary = summary.sort_values('LastRepTime').drop(['FirstRepTime','LastRepTime'],axis=1)
st.write(summary.tail(show_n))