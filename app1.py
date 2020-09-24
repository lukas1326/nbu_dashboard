import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Завантажити таблицю (.csv)</a>'
    return href

st.title("Показники фінансової діяльності банків України")
st.markdown("Дані фінансової звітності/згруповані балансові залишки банків України.")
st.markdown("Дані доступні з 01.02.2018 та формуються за станом на 01 число кожного місяця, млн грн")

st.sidebar.title("Фільтр по банкам України")
st.sidebar.markdown("Агреговані показники")


all_banks = st.sidebar.checkbox("Усі банки України", True)
# Вибір показника діяльності банків з верхнього рівня показників
id_tuple = [('Активи','BS1_AssetsTotal'),("Зобов'язання",'BS1_LiabTotal'),
('Капітал','BS1_CapitalTotal'),('Доходи і витрати - Всього доходів','BS1_IncomeTotal'),
('Доходи і витрати - Всього витрат','BS1_ExpenTotal'),('Доходи і витрати - Прибуток/(збиток) до оподаткування','BS1_ProfitLossBeforTax'),
('Доходи і витрати - Прибуток/(збиток) після оподаткування','BS1_ProfitLossAfterTax'),
('Відрахування до резервів','BS1_AllocProv')]

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



df_choice=pd.DataFrame(columns=['Дата',"Банк","Значення"])
df_con=pd.DataFrame(columns=['Дата',"Банк","Значення"])
df_all=pd.DataFrame(columns=['Дата',"Значення"])

if all_banks:
    df_all=df.groupby([df.dt]).value.sum().reset_index()
    df_all.columns = ['Дата',"Значення показника"]
    fig_1 = px.line(df_all, x='Дата', y='Значення показника', height=500,width=1000)
    st.plotly_chart(fig_1)
    st.markdown(get_table_download_link(df_all), unsafe_allow_html=True)

else:
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
    if st.sidebar.checkbox("Усі банки з державною часткою", False, key='0'):
        choice_A = list(name_list_A)
    else:
        choice_A = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_A))


    st.sidebar.subheader("Банки іноземних банківських груп")
    if st.sidebar.checkbox("Усі банки іноземних банківських груп", False, key='0'):
        choice_B = list(name_list_B)
    else:
        choice_B = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_B), key=1)


    st.sidebar.subheader("Банки з приватним капіталом")
    if st.sidebar.checkbox("Усі банки з приватним капіталом", False, key='0'):
        choice_E = list(name_list_E)
    else:
        choice_E = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_E), key=1)

    choice = choice_A+choice_B+choice_E

    if len(agg_choice)>0:
        df_con=df.groupby([df.dt,df.gr_bank]).value.sum().reset_index()
        df_con=df_con[df_con.gr_bank.isin(agg_choice)].reset_index()
        gr_bank=list(df_con['gr_bank'])


        a=[]
        for i in gr_bank:
            for j in agg_multi_select:
                if i.strip() ==j[1]:
                    a.append(j[0])
        df_con['gr_name']=pd.Series(a)
        df_con = df_con.loc[:,['dt','gr_name','value']]
        df_con.columns = ['Дата',"Банк","Значення"]



    if len(choice) >0:
        df_choice=df[df.fullname.isin(choice)]
        df_choice=df_choice.groupby([df.dt,df.fullname]).value.sum().reset_index()
        df_choice.columns = ['Дата',"Банк","Значення"]


    df_banks= pd.concat([df_choice,df_con],ignore_index=True)
    try:
        fig_2 = px.line(df_banks, x='Дата', y='Значення', color='Банк', height=500,width=1000)
        st.plotly_chart(fig_2)
    except:
        st.write('Заберіть позначку "Усі банки України" та оберіть банк чи групу банків')

#st.write(df_all)
#st.write(df)

# для завантаження таблиці у вигляді csv файлу


try:
    st.markdown(get_table_download_link(df_banks), unsafe_allow_html=True)
except:
    st.write('Заберіть позначку "Усі банки України" та оберіть банк чи групу банків')
