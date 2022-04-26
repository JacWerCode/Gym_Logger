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
st.set_page_config(layout="wide")
#from openpyxl import load_workbook
#import regex as re
from collections import defaultdict


session_exercises = pd.DataFrame()


def append_exercise(session_exercises,data):
    #st.write(data)
    pass 

def rearrange(list_object,target):
    return [list_object.pop(list_object.index(target))]+list_object

@st.cache
def load_exercises():    
    return  pd.read_csv('NS_Ref.csv').set_index('Exercise')

ref = load_exercises()

fill_in = ['Yeet']


exercise_data = {}



exercises = sorted(ref.index.unique())
exercise_data['Exercise'] = st.selectbox('Excersies',exercises)


exercise_data['Weight'] = st.number_input('Weight',0.,1000.,float(ref.loc[exercise_data['Exercise'],'Weight']),5.)


exercise_data['Sets'] =st.number_input('Sets',1,10,4,1)

rep_ranges = rearrange(sorted(ref['Reps'].unique()),ref.loc[exercise_data['Exercise'],'Reps'])
exercise_data['Reps'] = st.selectbox('Rep Range',rep_ranges)


st.button('Log excerise',on_click=append_exercise(session_exercises,exercise_data))

