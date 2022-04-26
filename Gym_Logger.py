# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 13:19:31 2022

@author: wersc
"""

import pandas as pd 
import numpy as np 
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
st.set_page_config(layout="wide")
#from openpyxl import load_workbook
#import regex as re
from collections import defaultdict


session_exercises = pd.DataFrame()


def append_exercise(session_exercises,data):
    #st.write(data)
    pass 



fill_in = ['Yeet']


exercise_data = {}


exercise_data['Exercise'] = st.selectbox('Excersies',fill_in)



exercise_data['Weight'] = st.number_input('Weight',0.,1000.,50.,5.)



set_input = ['8-10','10-12']
exercise_data['Sets'] = st.selectbox('Set Range',set_input)


st.write(exercise_data)

#st.button('Log excerise',on_click=append_exercise(session_exercises,exercise_data))

