# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 13:19:31 2022

@author: wersc
"""

import pandas as pd 
import numpy as np 
#import plotly.graph_objects as go
#import plotly.express as px
import streamlit as st
import datetime as dt
st.set_page_config(layout="wide")
#from openpyxl import load_workbook
#import regex as re
from collections import defaultdict


def rearrange(list_object,target):
    return [list_object.pop(list_object.index(target))]+list_object

@st.cache
def load_exercises():    
    return  pd.read_csv('NS_Ref.csv').set_index('Exercise')

ref = load_exercises()

exercises = sorted(ref.index.unique())


session_exercises = pd.DataFrame()




exercise_data = {}


person,ex,exercise = st.columns([1,1,6])


individuals = ['Nate','Selena','Jacob']

exercise_data['Individual'] = person.selectbox('Individual',individuals)

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

st.write(pd.DataFrame(exercise_data,index=[0]))    
