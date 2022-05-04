# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 13:19:31 2022

@author: wersc
"""

import pandas as pd 
import streamlit as st
import datetime as dt
st.set_page_config(layout="wide")

#import gspread
from dateutil import tz

def rearrange(list_object,target):
    return [list_object.pop(list_object.index(target))]+list_object

@st.cache
def load_exercises():    
    return  pd.read_csv('NS_Ref.csv').set_index('Exercise')

def load_db():
    return pd.read_csv('Data/DataBase.csv',parse_dates=True)

ref = load_exercises().reset_index()
db = load_db()

#main_link = 'https://docs.google.com/spreadsheets/d/1pVvJNRYqnsJVFHqFLNMehmCsQxqQagE_MKiH5Ue9T9c/edit?usp=sharing'

exercise_data = {}

user = st.columns([1])[0]
ex_type,exercise,exercise2,weight,reps,setType = st.columns([1,2,2,1,1,1])
notes = st.columns([1])[0]


individuals = ['Nate','Selena','Jacob']
exercise_data['User'] = user.selectbox('User',individuals)


ex_type_value = ex_type.selectbox('Muscle Group',sorted(ref['Body'].unique()))

body_ref = ref[ref['Body'] == ex_type_value]


ex_selection = exercise.selectbox('Exercise Selection',sorted(body_ref['Exercise'])+['Other'])

exercise_data['Body Part'] = ex_type_value

if ex_selection == 'Other':
    exercise_data['Exercise'] = exercise2.text_input('Exercise',placeholder='Type Exercise Here')
else:
    exercise_data['Exercise'] = ex_selection

 


exercise_data['Weight'] = weight.number_input('Weight',0.,1000.,50.0,2.5)
exercise_data['Reps'] = reps.number_input('Reps',1,50,8,1)
exercise_data['SetType'] = setType.selectbox('SetType',['Normal','To Failure','Superset',])

curr_time = dt.datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('America/Denver'))

exercise_data['DateTime'] = curr_time

exercise_data['Date']  = curr_time.date() #date.date_input('Day',value = )
exercise_data['Day'] = exercise_data['Date'].strftime('%A')[:3]
exercise_data['Time'] = curr_time.time().strftime("%H:%M:%S")
exercise_data['Notes'] = notes.text_input('Notes',placeholder='Type Notes here')


submit, rest,_ = st.columns([1,3,5])

if submit.button('Submit'):
    
    submitted_ex = pd.DataFrame(exercise_data,index=[0])
    
    db = pd.concat([db,submitted_ex],ignore_index=True).reset_index(drop=True)
    db.to_csv('Data/DataBase.csv',index=None)
    db = load_db()

if rest.button(f"Done with {exercise_data['Exercise']}"):
    exercise_data['Exercise'] = '---'
    exercise_data['Weight'] = 0
    db = pd.concat([db,pd.DataFrame(exercise_data,index=[0])],ignore_index=True).reset_index(drop=True)
    db.to_csv('Data/DataBase.csv',index=None)
    db = load_db()

def clear_history_button(db,exercise_data):
    if st.button('Clear User History'):
        user_mask = db['User'] == exercise_data['User']
        db = db[~user_mask]
        db.to_csv('Data/DataBase.csv',index=None)
    return db

db = clear_history_button(db,exercise_data)



db['Volume'] = db['Weight']*db['Reps']

user_mask = db['User'] == exercise_data['User']
user_df = db[user_mask].reset_index(drop=True)
user_df = user_df[user_df['Exercise'] != '---']

gby = user_df.groupby(['Date','Exercise'])[['Weight','Reps','Volume','Time']].agg(['min','max','sum','count']).reset_index()
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

#st.dataframe(user_df)
#st.dataframe(gby)

summary = summary.sort_values('LastRepTime').drop(['FirstRepTime','LastRepTime'],axis=1)
st.write(summary.tail(show_n))