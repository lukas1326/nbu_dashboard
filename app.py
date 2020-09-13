import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from banks import banks



st.title("Показники фінансової діяльності банків України")
st.sidebar.title("Фильтр по показателям и банкам")
st.markdown("Здесь что-то можно написать")
st.sidebar.markdown("щось написати")


name_pair=banks
name_list_A=[bank[0] for bank in banks if bank[2]=='A']
st.sidebar.subheader("Банки з державною часткою")
if st.sidebar.checkbox("Всі банки з державною часткою", False, key='0'):
    choice_A = name_list_A
else:
    choice_A = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_A), key=1)
st.sidebar.subheader("Банки іноземних банківських груп")
name_list_B=[bank[0] for bank in banks if bank[2]=='B']
if st.sidebar.checkbox("Всі банки іноземних банківських груп", False, key='0'):
    choice_B = name_list_B
else:
    choice_B = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_B), key=1)
st.sidebar.subheader("Банки з приватним капіталом")
name_list_E=[bank[0] for bank in banks if bank[2]=='E']
if st.sidebar.checkbox("Всі банки з приватним капіталом", False, key='0'):
    choice_E = name_list_E
else:
    choice_E = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_E), key=1)
choice = choice_A+choice_B+choice_E
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
