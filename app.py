import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from banks import banks



st.title("Тема проекта")
st.sidebar.title("Фильтр по показателям и банкам")
st.markdown("Здесь что-то можно написать")
st.sidebar.markdown("И здесь что-то можно написать")


name_pair=banks
name_list=[i[0] for i in name_pair]
choice = st.sidebar.multiselect('Pick bank', (name_list), key=0)

mfos=[i[1] for i in name_pair if i[0] in choice]


def get_data(mfo,id_api):
    BASE_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?mfo={mfo}&id_api={id_api}&start=20180101&period=m&json'
    url = BASE_URL.format(mfo=mfo,id_api=id_api)
    r = requests.get(url)
    source=r.json()
    return source

da=[]
for i in mfos:
    da+=get_data(i,id_api='BS1_AssetsCash')
df=pd.DataFrame(da)
df['dt']=pd.to_datetime(df.dt)
df=df.groupby([df.dt,df.mfo,df.fullname]).value.sum().reset_index()
fig_1 = px.line(df, x='dt', y='value', color='fullname', height=500,width=1000)
st.write("id_api='BS1_AssetsCash'")
st.plotly_chart(fig_1)
st.write(df)
