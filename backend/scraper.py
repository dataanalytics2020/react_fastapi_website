import requests
import bs4
import pandas as pd
import unicodedata
import string
from bs4 import BeautifulSoup
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

templates = Jinja2Templates(directory="templates")

def removal_text(text):
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans( '', '',string.punctuation  + '！'+ '　'+ ' '+'・'+'～' + '‐'))
    return text

class Scraper():
    def google_search(self, serch_tenpo_name,serch_date,request):
        # 指定したキーワードで検索
        search_url = url = f"https://ana-slo.com/{serch_date}-{serch_tenpo_name}-data/"
        search_response = requests.get(search_url)
        print(search_response)
        soup = BeautifulSoup(search_response.text, 'html.parser')
        dfs = pd.read_html(str(soup))
        for df in dfs:
            if '機種名' in list(df.columns):
                tmp_df = df
                tmp_df['店舗名'] = serch_tenpo_name
                tmp_df['機種名'] = tmp_df['機種名'].map(removal_text)
                break
        print(tmp_df)
        df_1 = tmp_df.to_html(index=False)
        templates.TemplateResponse("index.html", {"df_1": df_1,"request": request})
        data = HTMLResponse(content=templates.TemplateResponse("index.html", {"df_1": df_1,"request": request}))
        return templates.TemplateResponse("index.html", {"data": data})
