from bs4 import BeautifulSoup

import sqlite3 
conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
cur = conn.cursor()

import warnings
warnings.filterwarnings("ignore")


import pandas as pd
import xmltodict
import requests
import os
import json
import numpy as np
from datetime import datetime, timedelta
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
    
df_final = pd.DataFrame()    

for target_keyword in ["미래에셋증권",'키움증권','삼성증권','NH투자증권']:
    df_ttl = pd.DataFrame()
    new_html = requests.get('http://news.google.com/news?hl=ko&gl=kr&ie=UTF-8&output=rss&q=' + target_keyword )
    new_html.text
    soup = BeautifulSoup(new_html.text, 'html.parser')
    cnt = 0 
    news_title_l = []
    news_link_l = []
    news_writer_l = []
    url_l = []
    date_l = [] 

    for i in range(len(soup.findAll('item'))):
        news_title_l.append(soup.findAll('item')[i].find('title').text)
        news_link_l.append(str(soup.findAll('item')[i]).split('link/>')[1].split('<')[0])
        news_writer_l.append(    soup.findAll('item')[i].text.split(">")[-1])
        url_l.append(soup.findAll('item')[i].find('description').text.split('"')[1])
        date_l.append((datetime.strptime(soup.findAll('item')[i].find('pubdate').text, '%a, %d %b %Y %H:%M:%S GMT')+ timedelta(hours=9)).strftime('%Y%m%d-%H%M%S'))

        cnt +=1
        if cnt ==100:
            break

    df_ = pd.DataFrame()
    df_['news_title'] = news_title_l
    df_['news_link'] = news_link_l
    df_['news_writer'] = news_writer_l
    df_['news_url'] = url_l
    df_['date'] = date_l
    df_['CRAWLING_DATETIME'] = datetime.now().strftime('%Y%m%d-%H%M%S')


    df_['DATETIME'] = df_['date'] 
    df_['VIEWS'] = np.nan
    df_['LIKES'] = np.nan
    df_['TITLE'] =  df_['news_title']
    df_['CONTENT'] = np.nan
    df_['WRITER'] =df_['news_writer']

    df_['SOURCE'] = "구글뉴스"
    df_['RELATED_ITEM'] = target_keyword
    df_['POSITIVITY'] = np.nan

    df_['OTHERS'] = np.nan
    df_['NUM_REPLY'] = np.nan
    df_['CRAWLING_DATETIME'] = datetime.now().strftime('%Y%m%d-%H%M%S')
    df_['URL'] =  df_['news_url'] 
    df_ttl = df_ttl.append(df_[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]])
    
    df_already= pd.read_sql("SELECT * FROM TABLE_BUZZ where SOURCE  = '구글뉴스' and  RELATED_ITEM = '{}' ORDER BY DATETIME desc".format(target_keyword) ,conn)
    df_already

    df_ttl = df_ttl[~df_ttl['URL'].isin(df_already['URL'])].reset_index(drop=True)

    df_final = df_final.append(df_ttl)

if len(df_final) >0:

    df_final = df_final.reset_index(drop=True)
    for i in range(len(df_final)):
        df_final.loc[i,"POSITIVITY"] = get_sentiment(df_final.loc[i,"TITLE"])
    df_final
    df_final.to_sql('TABLE_BUZZ',conn,if_exists = 'append',index = False)
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')  , " GOOGLE NEWS - SUCCESS  : ",len(df_ttl))

else:
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , " GOOGLE NEWS - NO DATA TO UPDATE")
