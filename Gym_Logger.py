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


def rearrange(list_object,target):
    return [list_object.pop(list_object.index(target))]+list_object




@st.cache
def load_exercises():    
    return  pd.read_csv('NS_Ref.csv').set_index('Exercise')

def load_db():
    return pd.read_csv('Data/DataBase.csv')


ref = load_exercises()
db = load_db()

exercises = sorted(ref.index.unique())

#main_link = 'https://docs.google.com/spreadsheets/d/1pVvJNRYqnsJVFHqFLNMehmCsQxqQagE_MKiH5Ue9T9c/edit?usp=sharing'

exercise_data = {}

def append_user_exercise(user_df):
    pass


person,ex,exercise = st.columns([1,1,5])

individuals = ['Nate','Selena','Jacob']
exercise_data['User'] = person.selectbox('User',individuals)


existing_exercise = ex.selectbox('Exising Exercise',(True,False))

if existing_exercise:
    exercise_data['Exercise'] = exercise.selectbox('Exercise',exercises)
    start_weight = float(ref.loc[exercise_data['Exercise'],'Weight'])
    start_reps = ref.loc[exercise_data['Exercise'],'Reps']
else:
    exercise_data['Exercise'] = exercise.text_input('Exercise')
    start_weight=50.
    start_reps = '10-12'


weight, sets, reps = st.columns([1,1,1])

exercise_data['Weight'] = weight.number_input('Weight',0.,1000.,start_weight,5.)

exercise_data['Sets'] =sets.number_input('Sets',1,10,4,1)

rep_ranges = rearrange(sorted(ref['Reps'].unique()),start_reps)
exercise_data['Reps'] = reps.selectbox('Rep Range',rep_ranges)

if st.button('Submit'):
    exercise_data['Time'] = dt.datetime.now()
    
    submitted_ex = pd.DataFrame(exercise_data,index=[0])
    
    db = db.append(submitted_ex,ignore_index=True)
    
    db.to_csv('Data/DataBase.csv',index=None)
    
    
    user_mask = db['User'] == exercise_data['User']
    
    user_display = db[user_mask].tail().astype(str)
    
    st.write('Last 5 Exercises')
    st.dataframe(user_display)
    
    
    
