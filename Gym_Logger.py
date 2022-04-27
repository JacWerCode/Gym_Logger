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
import os

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
ex,exercise,weight = st.columns([1,3,1])





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
    start_reps = ref.loc[exercise_data['Exercise'],'Reps']
if ex_select == 'New Exercise':
    exercise_data['Exercise'] = exercise.text_input('Exercise',placeholder='Type exercise here')
    start_weight=50.
    start_reps = '10-12'




exercise_data['Weight'] = weight.number_input('Weight',0.,1000.,start_weight,5.)

#exercise_data['Sets'] =sets.number_input('Sets',1,10,4,1)

rep_ranges = rearrange(sorted(ref['Reps'].unique()),start_reps)



curr_time = dt.datetime.utcnow().replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('America/Denver'))

exercise_data['DateTime'] = curr_time
exercise_data['Date']  = curr_time.date() #date.date_input('Day',value = )
exercise_data['Day'] = exercise_data['Date'].strftime('%A')[:3]
exercise_data['Time'] = curr_time.time().strftime("%H:%M:%S")



submit, rest,_ = st.columns([1,1,8])

if submit.button('Submit Exercise'):
    
    
    submitted_ex = pd.DataFrame(exercise_data,index=[0])
    
    db = pd.concat([db,submitted_ex],ignore_index=True).reset_index(drop=True)
    db.to_csv('Data/DataBase.csv',index=None)
    db = load_db()
    


if rest.button("Add Rest"):
    exercise_data['Exercise'] = 'Rest'
    exercise_data['Weight'] = 0
    db = pd.concat([db,pd.DataFrame(exercise_data,index=[0])],ignore_index=True).reset_index(drop=True)
    db.to_csv('Data/DataBase.csv',index=None)
    db = load_db()

st.write('Last 5 Exercises')
user_mask = db['User'] == exercise_data['User']



if st.button('Clear User History'):
    db = db[~user_mask]
    db.to_csv('Data/DataBase.csv',index=None)



    

user_mask = db['User'] == exercise_data['User']
user_display = db[user_mask].tail().reset_index(drop=True)
st.write(user_display.drop('DateTime',axis=1).tail())
