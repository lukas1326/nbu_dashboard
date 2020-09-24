import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
#from banks import banks

import base64


st.title("Показники фінансової діяльності банків України")
st.markdown("Дані фінансової звітності/згруповані балансові залишки банків України.")
st.markdown("Дані доступні з 01.02.2018 та формуються за станом на 01 число кожного місяця, млн грн")

st.sidebar.title("Фільтр по банкам України")
st.sidebar.markdown("Агреговані показники")


all_banks = st.sidebar.checkbox("Всі банки України", True)
# Вибір показника діяльності банків з верхнього рівня показників
id_tuple = [('Активи','BS1_AssetsTotal'),("Зобов'язання",'BS1_LiabTotal'),
('Капітал','BS1_CapitalTotal'),('Доходи і витрати - Всього доходів','BS1_IncomeTotal'),
('Доходи і витрати - Всього витрат','BS1_ExpenTotal'),('Доходи і витрати - Прибуток/(збиток) до оподаткування','BS1_ProfitLossBeforTax'),
('Доходи і витрати - Прибуток/(збиток) після оподаткування','BS1_ProfitLossAfterTax')]

id_label = [i[0] for i in id_tuple]
id_choice = st.radio('Оберіть показник діяльності банку:',id_label)
id_api = [i[1] for i in id_tuple if i[0]==id_choice][0]

# обов'язково для даних,які будуть знову використовуватися в коді
@st.cache()
def get_bank_data():
    BASE_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?id_api={id_api}&start=20180101&period=m&json'
    url = BASE_URL.format(id_api=id_api)
    r = requests.get(url)
    source=r.json()
    return source
source=get_bank_data()

df=pd.DataFrame(source)
df=df[~(df.gr_bank=='F')].reset_index() #видаляємо групу неплатоспроможних банків-примітка експерта
df['dt']=pd.to_datetime(df.dt) #замінюємо формат дати

agg_multi_select = [('Банки з державною часткою',"A"),
('Банки іноземних банківських груп',"B"),
('Банки з приватним капіталом','E')]
agg_label = [i[0] for i in agg_multi_select]
agg_select = st.sidebar.multiselect('Оберіть групу банків для отримання агрегованого показника', (agg_label), key=1)
agg_choice = [i[1] for i in agg_multi_select if i[0] in agg_select]

name_list_A = df[df.gr_bank=="A"]['fullname'].unique()
name_list_B = df[df.gr_bank=="B"]['fullname'].unique()
name_list_E = df[df.gr_bank=="E"]['fullname'].unique()


st.sidebar.subheader("Банки з державною часткою")
if st.sidebar.checkbox("Всі банки з державною часткою", False, key='0'):
    choice_A = list(name_list_A)
else:
    choice_A = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_A))


st.sidebar.subheader("Банки іноземних банківських груп")
if st.sidebar.checkbox("Всі банки іноземних банківських груп", False, key='0'):
    choice_B = list(name_list_B)
else:
    choice_B = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_B), key=1)


st.sidebar.subheader("Банки з приватним капіталом")
if st.sidebar.checkbox("Всі банки з приватним капіталом", False, key='0'):
    choice_E = list(name_list_E)
else:
    choice_E = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_E), key=1)

choice = choice_A+choice_B+choice_E
st.write(choice)


if all_banks:
    df=df.groupby([df.dt]).value.sum().reset_index()
    df.columns = ['Дата',"Значення показника"]

if len(agg_choice)>0:
    df=df.groupby([df.dt,df.gr_bank]).value.sum().reset_index()
    df=df[df.gr_bank.isin(agg_choice)]
    df.columns = ['Дата',"Банк","Значення"]

if len(choice) >0:
    df=df[df.fullname.isin(choice)]
    df=df.groupby([df.dt,df.fullname]).value.sum().reset_index()
    df.columns = ['Дата',"Банк","Значення"]



st.write(df)

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