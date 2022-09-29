import sqlite3 
conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
cur = conn.cursor()

import re
from bs4 import BeautifulSoup
import requests
import itertools
from selenium.webdriver.support.ui import Select
import time
import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
client_id = "l5s8tg1g0w" # 개발자센터에서 발급받은 Client ID 값
client_secret = "RPNXQKCp8erMRW4KvKWsME5m3F9QOYVJTZ8Lvj56" # 개발자센터에서 발급받은 Client Secret 값


def get_sentiment(content):
    printout = True
    url="https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"

    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json"
    }

    data = {
      "content": content
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)
    rescode = response.status_code

    if(rescode == 200):        
        sentiment = json.loads(response.text)['document']['sentiment'] 
        pos_score = json.loads(response.text)['document']['confidence']['positive']
        neg_score = json.loads(response.text)['document']['confidence']['negative']
        neu_score = json.loads(response.text)['document']['confidence']['neutral']
#         if printout:
#             print("\n=== 감성분석 ===")
#             print("판정: {}\n점수: 긍정 {}, 중립 {}, 부정 {}".format(sentiment, pos_score, neu_score, neg_score)) 
#         return sentiment, pos_score, neu_score, neg_score
        return pos_score

    else:
        print("Error : " + response.text)
        return np.nan     
    
    
df_already= pd.read_sql("SELECT * FROM TABLE_BUZZ where SOURCE  = '네이버_종목토론실'",conn)
df_already



df_ttl = pd.DataFrame()

board_nm = 0

while True:
    board_nm +=1
    item_board_url = "https://finance.naver.com/item/board.naver?code=006800&page=" + str(board_nm)
    #         print(item_board_url)
    res = requests.get(item_board_url, headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'})#, params=params)
    soup = BeautifulSoup(res.text, "html5lib")
    #         tab_title = soup.findAll('td', attrs={'class':'title'})   
    tab_date = soup.findAll('span', attrs={'class':'tah p10 gray03'})  
    tab_date_txt = [i.text for i in tab_date]

    tab_title = soup.findAll('td', attrs={'class':'title'})  
    tab_title_txt = [i.text for i in tab_title]

    tab_writer = soup.findAll('td', attrs={'class':'p11'})  
    tab_writer_txt = [i.text for i in tab_writer]
    tab_writer_txt = tab_writer_txt[:len(tab_title_txt)]

    url_l = []
    for n in soup.findAll('td', attrs={'class':'title'})  :
        url_l.append("https://finance.naver.com/" +n.findAll('a')[0]['href'])
    url_l
    
    like_l = []
    for s in soup.findAll('tr'): 
        if len(s.findAll('strong')) > 0:
            like_l.append(s.findAll('strong')[0].text)
    like_l[:20]


    df_ = pd.DataFrame()
    df_['DATETIME'] = pd.Series(tab_date_txt).iloc[::2].reset_index(drop=True)
    df_['DATETIME'] =df_['DATETIME'].str.replace(".","").str.replace(" ","-").str.replace(":","")+"00"
    df_['VIEWS'] = pd.Series(tab_date_txt).iloc[1::2].reset_index(drop=True)
    df_['LIKES'] = like_l[:20]
    df_['TITLE'] =  pd.Series(tab_title_txt).str.replace('\n','').str.replace('\t','').reset_index(drop=True)
    df_['CONTENT'] = np.nan
    df_['WRITER'] = pd.Series(tab_writer_txt).str.replace('\n','').str.replace('\t','').reset_index(drop=True)

    df_['SOURCE'] = "네이버_종목토론실"
    df_['RELATED_ITEM'] = "미래에셋증권"
    df_['POSITIVITY'] = np.nan
    df_['OTHERS'] = df_[['WRITER']].to_dict('records')
    df_['OTHERS'] = df_['OTHERS'].astype(str)
    df_['NUM_REPLY'] = df_['TITLE'].apply(lambda x: x.split('[')[1].replace("]","") if len(x.split('[')) == 2 else 0)
    df_['CRAWLING_DATETIME'] = (datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')
    df_['URL'] =  url_l
    df_


    for i in range(len(df_)):
        df_.loc[i,"POSITIVITY"] = get_sentiment(df_.loc[i,"TITLE"])
    

    df_ = df_[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]]
    df_
    df_ttl = df_ttl.append(df_)
    if len(df_[df_['DATETIME']==df_already['DATETIME'].max()]) >0:
        break
        
    print(board_nm)
    
if len(df_ttl) >0:
    df_ttl = df_ttl.iloc[:df_ttl[df_ttl['DATETIME']==df_already['DATETIME'].max()].index[0]]
    if len(df_ttl) >0:
        df_ttl = df_ttl.reset_index(drop=True)

        df_ttl
        df_ttl.to_sql('TABLE_BUZZ',conn,if_exists = 'append',index = False)
        print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , " SUCCESS  : ",len(df_ttl))
    else:
        print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S'), " NO DATA TO UPDATE")
else:
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S'), " NO DATA TO UPDATE")

