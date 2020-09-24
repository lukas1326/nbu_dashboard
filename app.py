import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from banks import banks

import base64


st.title("Показники фінансової діяльності банків України")
st.sidebar.title("Фільтр по банкам України")
st.markdown("Дані фінансової звітності/згруповані балансові залишки банків України.")
st.markdown("Дані доступні з 01.02.2018 та формуються за станом на 01 число кожного місяця, млн грн")
st.sidebar.markdown("щось написати")

# обов'язково для даних,які будуть знову використовуватися в коді
@st.cache
def get_bank_data():
    name_pair=banks
    return name_pair
name_pair=get_bank_data()

# агреговані показники по всім банкам України
all_banks = st.sidebar.checkbox("Всі банки України", True)


# обираємо банки за категорією "Всі банки з державною часткою"
name_list_A=[bank[0] for bank in banks if bank[2]=='A']
st.sidebar.subheader("Банки з державною часткою")
if st.sidebar.checkbox("Всі банки з державною часткою", False, key='0'):
    choice_A = name_list_A
else:
    choice_A = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_A))


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


# Вибір показника діяльності банків з верхнього рівня показників
id_tuple = [('Активи','BS1_AssetsTotal'),("Зобов'язання",'BS1_LiabTotal'),
('Капітал','BS1_CapitalTotal'),('Доходи і витрати - Всього доходів','BS1_IncomeTotal'),
('Доходи і витрати - Всього витрат','BS1_ExpenTotal'),('Доходи і витрати - Прибуток/(збиток) до оподаткування','BS1_ProfitLossBeforTax'),
('Доходи і витрати - Прибуток/(збиток) після оподаткування','BS1_ProfitLossAfterTax')]

id_label = [i[0] for i in id_tuple]
id_choice = st.radio('Оберіть показник діяльності банку:',id_label)
id_api = [i[1] for i in id_tuple if i[0]==id_choice][0]


def get_data(mfo,id_api):
    BASE_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?mfo={mfo}&id_api={id_api}&start=20180101&period=m&json'
    url = BASE_URL.format(mfo=mfo,id_api=id_api)
    r = requests.get(url)
    source=r.json()
    return source
def get_data_all(id_api):
    BASE_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?id_api={id_api}&start=20180101&period=m&json'
    url = BASE_URL.format(id_api=id_api)
    r = requests.get(url)
    source=r.json()
    return source

if all_banks:
    source=get_data_all(id_api)
    df=pd.DataFrame(source)
    df['dt']=pd.to_datetime(df.dt)
    df=df.groupby([df.dt]).value.sum().reset_index()
    df.columns = ['Дата',"Значення"]
    fig_1 = px.line(df, x='Дата', y='Значення', height=500,width=1000)
    st.plotly_chart(fig_1)
    st.write(df)
else:
    if len(choice)>0:
        da=[]
        for i in mfos:
            da+=get_data(i,id_api=id_api)
        df=pd.DataFrame(da)
        df['dt']=pd.to_datetime(df.dt)
        df=df.groupby([df.dt,df.mfo,df.fullname]).value.sum().reset_index()
        df.columns = ['Дата',"МФО","Назва","Значення"]
        fig_1 = px.line(df, x='Дата', y='Значення', color='Назва', height=500,width=1000)
        st.plotly_chart(fig_1)
        st.write(df)

#print('Оберіть банк чи групу банків')

# для завантаження таблиці у вигляді csv файлу

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Завантажити таблицю (.csv)</a>'
    return href
try:
    st.markdown(get_table_download_link(df), unsafe_allow_html=True)
except:
    st.write('Оберіть банк чи групу банків')
