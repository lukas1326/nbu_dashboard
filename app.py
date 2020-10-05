import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
from banks import banks

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
# Вибір показника діяльності банків з верхнього рівня показників та по запиту
id_tuple = [('Активи','BS1_AssetsTotal'),("Зобов'язання",'BS1_LiabTotal'),
('Капітал','BS1_CapitalTotal'),('Доходи і витрати - Всього доходів','BS1_IncomeTotal'),
('Доходи і витрати - Всього витрат','BS1_ExpenTotal'),('Доходи і витрати - Прибуток/(збиток) до оподаткування','BS1_ProfitLossBeforTax'),
('Доходи і витрати - Прибуток/(збиток) після оподаткування','BS1_ProfitLossAfterTax'),
('Відрахування до резервів','BS1_AllocProv'),('Прибуток/(збиток) до оподаткування без впливу резервів','BS1_ProfitLossBeforTax_PLUS_BS1_AllocProv'),
('Чистий процентний дохід/(Чисті процентні витрати)','BS1_NetInterIncomeCosts'),('Чистий комісійний дохід/(Чисті комісійні витрати)','BS1_NetCommIncomeCosts'),
('Активи - Резерви під знецінення кредитів та заборгованості клієнтів','AssetsProvLoans')]

id_label = [i[0] for i in id_tuple]
id_choice = st.radio('Оберіть показник діяльності банку:',id_label)
id_api = [i[1] for i in id_tuple if i[0]==id_choice][0]


# обов'язково для даних,які будуть знову використовуватися у коді
@st.cache(persist=True)
def get_bank_data():
    BASE_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?id_api={id_api}&start=20180101&period=m&json'
    url = BASE_URL.format(id_api=id_api)
    r = requests.get(url)
    source=r.json()
    df=pd.DataFrame(source)
    df=df[~(df.gr_bank=='F')].reset_index() #видаляємо групу неплатоспроможних банків-примітка експерта
    df['dt']=pd.to_datetime(df.dt)
    return df


id_api1='BS1_ProfitLossBeforTax'
id_api2='BS1_AllocProv'
@st.cache(persist=True)
def get_bank_data_custom():
    BASE_URL1 = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?id_api={id_api}&start=20180101&period=m&json'
    url1= BASE_URL1.format(id_api=id_api1)
    url2= BASE_URL1.format(id_api=id_api2)
    r1 = requests.get(url1)
    r2 = requests.get(url2)
    source1=r1.json()
    source2=r2.json()
    source3=source1+source2
    df1 = pd.DataFrame(source3)
    df1['dt']=pd.to_datetime(df1.dt)
    df_pivot=df1.pivot_table(index=['dt','gr_bank','fullname'],columns='id_api',values='value').reset_index()
    df_pivot['BS1_ProfitLossBeforTax_PLUS_BS1_AllocProv']=df_pivot.BS1_ProfitLossBeforTax+df_pivot.BS1_AllocProv
    df_pivot.columns.name=''
    df_pivot=df_pivot.drop(columns=['BS1_AllocProv','BS1_ProfitLossBeforTax'])
    df=df_pivot.copy()
    df.columns=['dt','gr_bank','fullname','value']
    df['id_api']='BS1_ProfitLossBeforTax_PLUS_BS1_AllocProv'
    #df.loc[:,['dt','gr_bank','fullname','id_api','value']]
    df=df[~(df.gr_bank=='F')].reset_index()
    return df


id_api3='BS1_AssetsProvLoansLE'
id_api4='BS1_AssetsProvLoansIndiv'
@st.cache(persist=True)
def get_bank_data_AssetsProvLoans():
    BASE_URL1 = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?id_api={id_api}&start=20180101&period=m&json'
    url1= BASE_URL1.format(id_api=id_api3)
    url2= BASE_URL1.format(id_api=id_api4)
    r1 = requests.get(url1)
    r2 = requests.get(url2)
    source1=r1.json()
    source2=r2.json()
    source3=source1+source2
    df1 = pd.DataFrame(source3)
    df1['dt']=pd.to_datetime(df1.dt)
    df1=df1[~(df1.gr_bank=='F')].reset_index()
    df_concat=df1.groupby(['dt','id_api','fullname','gr_bank']).value.sum().reset_index()
    df_concat=df_concat.pivot_table(index=['dt','gr_bank','fullname'],columns='id_api',values='value').reset_index()
    df_concat=df_concat.apply(lambda x: x.fillna(0))
    df_concat['BS1_AssetsProvLoansIndiv_PLUS_BS1_AssetsProvLoansLE']=df_concat['BS1_AssetsProvLoansIndiv']+df_concat['BS1_AssetsProvLoansLE']
    df_concat1=df_concat.T.reset_index(drop=True).T
    df_concat1.columns=['dt','gr_bank','fullname','BS1_AssetsProvLoansIndiv','BS1_AssetsProvLoansLE','BS1_AssetsProvLoansIndiv_PLUS_BS1_AssetsProvLoansLE']
    df_pic=pd.melt(df_concat1, id_vars=['dt','gr_bank','fullname'], value_vars=['BS1_AssetsProvLoansIndiv','BS1_AssetsProvLoansLE','BS1_AssetsProvLoansIndiv_PLUS_BS1_AssetsProvLoansLE'],
        var_name='id_api', value_name='value')
    df_pic['value']=df_pic.value*(-1)
    return df_pic

  
labels={"BS1_AssetsProvLoansIndiv":"Резерви під знецінення кредитів та заборгованості клієнтів-фізичних осіб",
                        "BS1_AssetsProvLoansLE":"Резерви під знецінення кредитів та заборгованості клієнтів-юридичних осіб",
                        "BS1_AssetsProvLoansIndiv_PLUS_BS1_AssetsProvLoansLE":"Резерви під знецінення кредитів та заборгованості клієнтів"}
   


# списки для трьох груп банків
name_list_A=[bank[0] for bank in banks if bank[2]=='A']
name_list_B=[bank[0] for bank in banks if bank[2]=='B']
name_list_E=[bank[0] for bank in banks if bank[2]=='E']

# пусті датафрейми
df_choice=pd.DataFrame(columns=['Дата',"Банк","Показник","Значення"])
df_con=pd.DataFrame(columns=['Дата',"Банк","Показник","Значення"])
df_all=pd.DataFrame(columns=['Дата',"Показник","Значення"])

# вибір агрегованих показників по трьом групам банків
agg_multi_select = [('Банки з державною часткою',"A"),
    ('Банки іноземних банківських груп',"B"),
    ('Банки з приватним капіталом','E')]
agg_label = [i[0] for i in agg_multi_select]
agg_select = st.sidebar.multiselect('Оберіть групу банків для отримання агрегованого показника', (agg_label), key=1)
agg_choice = [i[1] for i in agg_multi_select if i[0] in agg_select]



st.sidebar.subheader("Банки з державною часткою")
if st.sidebar.checkbox("Усі банки з державною часткою", False, key='0'):
    choice_A = name_list_A
else:
    choice_A = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', name_list_A)


st.sidebar.subheader("Банки іноземних банківських груп")
if st.sidebar.checkbox("Усі банки іноземних банківських груп", False):
        choice_B = name_list_B
else:
    choice_B = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', name_list_B)


st.sidebar.subheader("Банки з приватним капіталом")
if st.sidebar.checkbox("Усі банки з приватним капіталом", False):
    choice_E = list(name_list_E)
else:
    choice_E = st.sidebar.multiselect('Вибрати банк чи де-кілька банків', (name_list_E))

choice = choice_A+choice_B+choice_E


if id_api=='BS1_ProfitLossBeforTax_PLUS_BS1_AllocProv':
    df=get_bank_data_custom()
elif id_api=='AssetsProvLoans':
    df=get_bank_data_AssetsProvLoans()
else:
    df=get_bank_data()

if all_banks:
    if id_api=='AssetsProvLoans':
        df_all=df.groupby([df.dt,df.id_api]).value.sum().reset_index()
        df_all.columns = ['Дата',"Показник","Значення показника"]
        df_all['Показник']=df_all["Показник"].replace(labels)
        fig_1 = px.line(df_all, x='Дата', y='Значення показника',facet_col="Показник", height=500,width=1000,
            title='Графік агрегованих показників по всім банках України',template="plotly_white",
        facet_col_spacing=0.04,
        category_orders={
                        "Показник": ["Резерви під знецінення кредитів та заборгованості клієнтів-фізичних осіб", 
                        "Резерви під знецінення кредитів та заборгованості клієнтів-юридичних осіб",
                        "Резерви під знецінення кредитів та заборгованості клієнтів"]})
       
        
        fig_1.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_1.for_each_annotation(lambda a: a.update(text=a.text[:31]+'<br>'+a.text[31:50]+'<br>'+a.text[50:]))
        fig_1.update_layout(
            title={
            'y':1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        
        st.plotly_chart(fig_1)
        st.markdown(get_table_download_link(df_all), unsafe_allow_html=True)
    else:
        df_all=df.groupby([df.dt]).value.sum().reset_index()
        df_all.columns = ['Дата',"Значення показника"]
        fig_1 = px.line(df_all, x='Дата', y='Значення показника', height=500,width=1000,
            title='Графік агрегованих показників по всім банках України',template="plotly_white")
        st.plotly_chart(fig_1)
        st.markdown(get_table_download_link(df_all), unsafe_allow_html=True)

if len(choice) >0:
    df_choice=df[df.fullname.isin(choice)].reset_index()
    df_choice=df_choice.groupby([df_choice.dt,df_choice.fullname,df_choice.id_api]).value.sum().reset_index()
    df_choice.columns = ['Дата',"Банк",'Показник',"Значення"]

if len(agg_choice)>0:
    
    df_con=df.groupby([df.dt,df.gr_bank,df.id_api]).value.sum().reset_index()
    df_con=df_con[df_con.gr_bank.isin(agg_choice)].reset_index()
    gr_bank=list(df_con['gr_bank'])


    a=[]
    for i in gr_bank:
        for j in agg_multi_select:
            if i.strip() ==j[1]:
                a.append(j[0])
    df_con['gr_name']=pd.Series(a)
    df_con = df_con.loc[:,['dt','gr_name','id_api','value']]
    df_con.columns = ['Дата',"Банк",'Показник',"Значення"]


df_banks= pd.concat([df_choice,df_con],ignore_index=True)


if id_api=='AssetsProvLoans':
    try:
        df_banks['Показник']=df_banks["Показник"].replace(labels)
        fig_2 = px.line(df_banks, x='Дата', y='Значення', color='Банк', facet_col='Показник', height=500,width=1000,template="plotly_white",
        title='Графік показників банків чи груп банків',
        facet_col_spacing=0.04,
        category_orders={
                        "Показник": ["Резерви під знецінення кредитів та заборгованості клієнтів-фізичних осіб", 
                        "Резерви під знецінення кредитів та заборгованості клієнтів-юридичних осіб",
                        "Резерви під знецінення кредитів та заборгованості клієнтів"]}
        )
        
        fig_2.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        fig_2.for_each_annotation(lambda a: a.update(text=a.text[:31]+'<br>'+a.text[31:50]+'<br>'+a.text[50:]))
        fig_2.update_layout(
            title={
            'y':1,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
        st.plotly_chart(fig_2)
    except:
        st.write('Заберіть позначку "Усі банки України" та оберіть банк чи групу банків')
    # для завантаження таблиці у вигляді csv файлу
    try:
        st.markdown(get_table_download_link(df_banks), unsafe_allow_html=True)
    except:
        st.write('Заберіть позначку "Усі банки України" та оберіть банк чи групу банків')
else:
    try:
        fig_2 = px.line(df_banks, x='Дата', y='Значення', color='Банк', height=500,width=1000,template="plotly_white",
        title='Графік показників банків чи груп банків')
        st.plotly_chart(fig_2)
    except:
        st.write('Заберіть позначку "Усі банки України" та оберіть банк чи групу банків')
    # для завантаження таблиці у вигляді csv файлу
    try:
        st.markdown(get_table_download_link(df_banks), unsafe_allow_html=True)
    except:
        st.write('Заберіть позначку "Усі банки України" та оберіть банк чи групу банків')


