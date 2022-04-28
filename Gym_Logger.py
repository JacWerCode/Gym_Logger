# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 13:19:31 2022

@author: wersc
"""

import pandas as pd 
#import numpy as np 
#import plotly.graph_objects as go
#import plotly.express as px
import streamlit as st
import datetime as dt
st.set_page_config(layout="wide")
#from openpyxl import load_workbook
#import regex as re
#from collections import defaultdict

#import gspread
from dateutil import tz

def rearrange(list_object,target):
    return [list_object.pop(list_object.index(target))]+list_object




@st.cache
def load_exercises():    
    return  pd.read_csv('NS_Ref.csv').set_index('Exercise')

def load_db():
    return pd.read_csv('Data/DataBase.csv',parse_dates=True)


ref = load_exercises()
db = load_db()

exercises = sorted(ref.index.unique())

#main_link = 'https://docs.google.com/spreadsheets/d/1pVvJNRYqnsJVFHqFLNMehmCsQxqQagE_MKiH5Ue9T9c/edit?usp=sharing'

exercise_data = {}

def append_user_exercise(user_df):
    pass


user_exists, user = st.columns([1,4])
#date, time = st.columns([1,1])
ex,exercise,weight,reps,setType = st.columns([1,2,1,1,1])





if user_exists.selectbox('New User', (False,True)):
    exercise_data['User'] = user.text_input('User',placeholder='Type Name Here')
else:
    individuals = ['Nate','Selena','Jacob']
    exercise_data['User'] = user.selectbox('User',individuals)

# = time.time_input('Time',value=datetime.time()).strftime("%I:%M:%S %p")

ex_select = ex.selectbox('Exercise Source',('Existing Exercise','New Exercise'))

if ex_select=='Existing Exercise':
    exercise_data['Exercise'] = exercise.selectbox('Exercise',exercises)
    start_weight = float(ref.loc[exercise_data['Exercise'],'Weight'])
#    start_reps = ref.loc[exercise_data['Exercise'],'Reps']
if ex_select == 'New Exercise':
    exercise_data['Exercise'] = exercise.text_input('Exercise',placeholder='Type exercise here')
    start_weight=50.
#    start_reps = '10-12'

exercise_data['Weight'] = weight.number_input('Weight',0.,1000.,start_weight,5.)
exercise_data['Reps'] = reps.number_input('Reps',1,50,8,1)
exercise_data['SetType'] = setType.selectbox('SetType',['Normal','To Failure','Superset',])

curr_time = dt.datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('America/Denver'))

exercise_data['DateTime'] = curr_time

exercise_data['Date']  = curr_time.date() #date.date_input('Day',value = )
exercise_data['Day'] = exercise_data['Date'].strftime('%A')[:3]
exercise_data['Time'] = curr_time.time().strftime("%H:%M:%S")



submit, rest,_ = st.columns([1,4,5])

if submit.button('Submit Exercise'):
    
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

if st.button('Clear User History'):
    user_mask = db['User'] == exercise_data['User']
    db = db[~user_mask]
    db.to_csv('Data/DataBase.csv',index=None)

#.write('Last 5 Exercises')
db['Volume'] = db['Weight']*db['Reps']

user_mask = db['User'] == exercise_data['User']
user_df = db[user_mask]
#user_display = user_df.reset_index(drop=True)
#st.dataframe(user_display.drop('DateTime',axis=1))

user_df['TimeSpent'] = 0
user_df['SetID'] = 0
set_id = 0
for i in user_df.index[1:]:
    if user_df.loc[i,'Exercise'] !=  user_df.loc[i-1,'Exercise']:
        set_id+=1
    user_df.loc[i,'SetID'] = set_id
    user_df.loc[i-1,'TimeSpent'] = (dt.datetime.fromisoformat(user_df.loc[i,'DateTime']) - dt.datetime.fromisoformat(user_df.loc[i-1,'DateTime'])).seconds


user_df = user_df[user_df['Exercise'] != '---']

gby = user_df.groupby(['Date','SetID','Exercise'])['Weight','Reps','Volume','TimeSpent'].agg(['min','max','sum','count']).reset_index()
gby.columns = [f'{stat}{metric}' for metric, stat in gby.columns]

#gby['maxDateTime'] = gby['maxDateTime'].apply(lambda x: dt.datetime.fromisoformat(x))
#gby['minDateTime'] = gby['minDateTime'].apply(lambda x: dt.datetime.fromisoformat(x))

if len(gby) > 0:

    summary = pd.DataFrame()
    summary['Date'] = gby['Date']
    summary['Exercise'] = gby['Exercise']
    summary['Weight'] = gby['minWeight'].astype(str) +" - "+ gby['maxWeight'].astype(str)
    summary['Weight'] = summary['Weight'].apply(lambda x: x.split(" - ")[0] if x.split(" - ")[0]==x.split(" - ")[1] else x)
    summary['Reps'] = gby['minReps'].astype(str) +" - "+ gby['maxReps'].astype(str)
    summary['Reps'] = summary['Reps'].apply(lambda x: x.split(" - ")[0] if x.split(" - ")[0]==x.split(" - ")[1] else x)
    
    summary['Sets'] = gby['countWeight']
    summary['TotalReps'] = gby['sumReps'].astype(str)
    summary['TotalVolume'] = gby['sumVolume'].astype(str)
    summary['Time'] = gby['sumTimeSpent'].astype(str)
    
    #st.dataframe(user_df)
    #st.dataframe(gby)
    st.dataframe(summary.tail())