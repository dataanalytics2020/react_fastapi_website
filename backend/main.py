from fastapi import FastAPI, Request
from starlette.requests import Request
from scraper import Scraper
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import requests
import bs4
import pandas as pd
import unicodedata
import string
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from datetime import date, timedelta

app = FastAPI()
scraper = Scraper()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")



# @app.get("/{serch_date}-{serch_tenpo_name}-data/",response_class=HTMLResponse)
# async def search_google(serch_tenpo_name,serch_date, request: Request):
#     return scraper.google_search(serch_tenpo_name,serch_date,request)
def removal_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans( '', '',string.punctuation  + '！'+ '　'+ ' '+'・'+'～' + '‐'))
    return text


@app.get("/{serch_tenpo_name}-{target_n_day}-{n_times}/",response_class=HTMLResponse)
async def search_google(serch_tenpo_name,target_n_day,n_times, request: Request):
    from datetime import date, timedelta
    target_number = str(target_n_day)
    print()
    target_day_list = []
    number = 0
    for i in range(int(n_times)):
        while True:
            print(number)
            if target_number == str(date.today() - timedelta(days=number))[-1]:
                target_day = date.today() - timedelta(days=number)
                print('取得日',target_day)
                target_day_str = target_day.strftime('%Y-%m-%d')
                target_day_list.append(target_day_str)
                number += 1
                break
            else: 
                pass
            number += 1
    target_day_list   
    concat_df_list = []
    urls = []
    for serch_date in target_day_list:
        search_url = url = f"https://ana-slo.com/{serch_date}-{serch_tenpo_name}-data/"
        urls.append(search_url)
        #search_response = requests.get(search_url)
        #print(search_response)
        # soup = BeautifulSoup(search_response.text, 'html.parser')
        # dfs = pd.read_html(str(soup))
        # for df in dfs:
        #     if '機種名' in list(df.columns):
        #         tmp_df = df
        #         tmp_df['店舗名'] = serch_tenpo_name
        #         tmp_df['機種名'
    with ThreadPoolExecutor(3) as executor:
        results = list(executor.map(requests.get, urls))
    print(results)

    concat_df_list = []
    for search_response,date in zip(results, target_day_list):
        
        soup = BeautifulSoup(search_response.text, "lxml")
        elem = soup.select('#all_data_block')
        dfs = pd.read_html(str(elem))
        for df in dfs:
            if '機種名' in list(df.columns):
                tmp_df = df
                tmp_df['店舗名'] = serch_tenpo_name
                tmp_df['日付'] = date
                #tmp_df['機種名'] = tmp_df['機種名'].map(removal_text)
                break
        concat_df_list.append(df)

    concat_df = pd.concat(concat_df_list,axis=0)
    concat_df = concat_df.groupby(['日付','機種名']).mean().sort_values('差枚',ascending=False)
    concat_df = concat_df[['G数','差枚']]
    concat_df['差枚'] =concat_df['差枚'].astype(int)
    concat_df['G数'] =concat_df['G数'].astype(int)
    concat_df = concat_df.reset_index()
    concat_df_html = concat_df.to_html(index=False)
     
    return  concat_df_html

@app.get("/", response_class=HTMLResponse)
def get_product(request: Request):
    return templates.TemplateResponse(
            "index.html",
            {
                "request": requests
            }
        )
    
@app.get("/hello/", response_class=HTMLResponse)
async def hello(request: Request):
   return templates.TemplateResponse("hello.html", {"request": request})