import json
import requests
import re
import pandas as pd
import numpy as np
import datetime
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

from bs4 import BeautifulSoup, BeautifulStoneSoup

import sqlite3 
conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
cur = conn.cursor()


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

df_already = pd.read_sql("SELECT OTHERS FROM TABLE_BUZZ where SOURCE = 'dcinside_미국주식갤러리' ORDER BY DATETIME desc limit 1",conn)


start_id = eval(df_already['OTHERS'][0])['boards_ID']+ 1 #4630000#
start_id

err_cnt = 0
boards_ID_l = []
boards_title_l = []
board_main_l = []
board_read_l = []
board_recommend_l = []
board_reply_l = []
board_writer_l = []
board_writerip_l = []
board_time_l = []
board_crawl_time_l = []
board_url_l = []
while True:
    try:

        headers = [
        {'User-Agent' : '' },

        ]
        BASE_URL = 'https://gall.dcinside.com/mgallery/board/view/?id=stockus&no=' + str(start_id)
        response = requests.get(BASE_URL,  headers=headers[0])

        soup = BeautifulSoup(response.content, 'html.parser')
        boards_ID = start_id
        boards_title    = soup.find('title').text.replace(' - 미국 주식 마이너 갤러리','')
        board_main      = soup.find('div', {"class": "write_div"}).text.replace('\n','')
        board_read      = int(soup.find('span', {"class": "gall_count"}).text.replace('조회 ',''))
        board_recommend = int(soup.find('span', {"class": "gall_reply_num"}).text.replace('추천 ',''))
        board_reply     = int(soup.find('span', {"class": "gall_comment"}).text.replace('댓글 ',''))
        board_writer    = soup.find('span', {"class": "nickname"}).text
        board_writerip  = soup.find('span', {"class": "ip"}).text
        board_time      = soup.find('span', {"class": "gall_date"}).text
        board_url= BASE_URL
#         print(boards_ID, "//", boards_title, '/',board_main, '/',board_read, '/',board_recommend , '/',board_reply , '/',board_writer, '/',board_url, '/',board_time, '/',
#           )
        start_id += 1

        boards_ID_l.append(boards_ID) 
        boards_title_l.append(boards_title) 
        board_main_l.append(board_main) 
        board_read_l.append(board_read) 
        board_recommend_l.append(board_recommend) 
        board_reply_l.append(board_reply) 
        board_writer_l.append(board_writer) 
        board_writerip_l.append(board_writerip) 
        board_time_l.append(board_time) 
        board_crawl_time_l.append(datetime.now())
        board_url_l.append(board_url)


        err_cnt = 0
    except:
#         print(start_id,'err')
        err_cnt +=1
        start_id += 1


        if err_cnt > 50:
            break
    time.sleep(0.7)

df_ = pd.DataFrame()
df_['boards_ID'] = boards_ID_l 
df_['boards_title'] = boards_title_l 
df_['board_main'] = board_main_l 
df_['board_read'] = board_read_l 
df_['board_recommend'] = board_recommend_l 
df_['board_reply'] = board_reply_l 
df_['board_writer'] = board_writer_l 
df_['board_writerip'] = board_writerip_l 
df_['board_time'] = board_time_l 
df_['board_time'] = df_['board_time'].apply(lambda x :  datetime.strptime(x, '%Y.%m.%d %H:%M:%S')) 
df_['board_crawl_time'] =  board_crawl_time_l
df_['board_url'] =  board_url_l
df_['source'] = 'dc_gall'
df_['updated'] = (datetime.now() + timedelta(hours=9)).strftime("%Y%m%d-%H%M%S")

df_['DATETIME'] = df_['board_time'].apply(lambda x :  x.strftime("%Y%m%d-%H%M%S") ) 
df_['VIEWS'] = df_['board_read']
df_['LIKES'] = df_['board_recommend']
df_['TITLE'] =  df_['boards_title']
df_['CONTENT'] = df_['board_main']
df_['WRITER'] =df_['board_writer']
df_['SOURCE'] = "dcinside_미국주식갤러리"
df_['RELATED_ITEM'] = np.nan
df_['POSITIVITY'] = np.nan
for i in range(len(df_)):
    df_.loc[i,"POSITIVITY"] = get_sentiment(df_.loc[i,"TITLE"])
    
df_['OTHERS'] = df_[['boards_ID','board_reply','board_writerip']].to_dict('records')
df_['OTHERS'] = df_['OTHERS'].astype(str)

df_['NUM_REPLY'] = df_['board_reply'] 
df_['CRAWLING_DATETIME'] =df_['updated'] 
df_['URL'] =  df_['board_url']
df_ttl = df_[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]]

if len(df_ttl) >0:
    df_ttl = df_ttl.reset_index(drop=True)

    df_ttl.to_sql('TABLE_BUZZ',conn,if_exists = 'append',index = False)
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , " DC_US-STOCK , SUCCESS  : ",len(df_ttl))

else:
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , " DC_US-STOCK , NO DATA TO UPDATE")