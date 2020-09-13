import requests
from datetime import timedelta
from datetime import date
from datetime import datetime

def last_report(today):
    BASE_URL = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/banksfinrep?date={date}&period=m&json'
    month = today.month
    year = today.year

    if month in range(10,11,12):
        date=f"{year}{month}01"
    else:
        date=f"{year}0{month}01"

    url = BASE_URL.format(date=date)
    r = requests.get(url)
    return r,url

today=datetime.today()
while True:
    try:
        r,url=last_report(today)
        while r.status_code !=200:
            today=today-timedelta(days=1)
            r,url=last_report(today)# try code
        break # quit the loop if successful
    except:
        print("No connection with API")# error handling

r = requests.get(url)
source=r.json()
name_pair = [(i['fullname'],i['mfo'],i['gr_bank']) for i in source]
banks = list(set(name_pair))
