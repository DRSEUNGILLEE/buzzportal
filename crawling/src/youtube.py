from selenium.webdriver.common.by import By
import requests
import re
import pandas as pd
import numpy as np
import datetime
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import warnings
warnings.filterwarnings('ignore')
import sqlite3
from bs4 import BeautifulSoup, BeautifulStoneSoup
import json
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('window-size=1920,1080')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent={0}'.format(user_agent))
# options =  webdriver.Chrome('/home/porter/NOTEBOOK/chromedriver',options=options)
conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
cur = conn.cursor()

client_id = "l5s8tg1g0w" # 개발자센터에서 발급받은 Client ID 값
client_secret = "RPNXQKCp8erMRW4KvKWsME5m3F9QOYVJTZ8Lvj56" # 개발자센터에서 발급받은 Client Secret 값

from datetime import datetime, timedelta

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
    
    
    
driver = webdriver.Chrome('/home/buzzportal/crawling/chromedriver',options=options)    
# driver = webdriver.Chrome('/home/lsi8505/chromedriver',options=options)
driver.get("https://www.youtube.com/c/SmartMoney0/videos")
time.sleep(10)

html= driver.page_source
html_res = BeautifulSoup(html, "html.parser") 
res_data_table =  html_res.find_all("ytd-grid-video-renderer")[1]
videos_l = []
for vid in range(len(html_res.find_all("ytd-grid-video-renderer"))):
    if ("1 day ago" in html_res.find_all("ytd-grid-video-renderer")[vid].find_all("span", {"class": "style-scope ytd-grid-video-renderer"})[1].text) & ("11" not in html_res.find_all("ytd-grid-video-renderer")[vid].find_all("span", {"class": "style-scope ytd-grid-video-renderer"})[1].text):
        
        sub_url = html_res.find_all("ytd-grid-video-renderer")[vid].find_all("a", {"class": "yt-simple-endpoint style-scope ytd-grid-video-renderer"})[0]['href']
        videos_l.append("https://www.youtube.com{}".format( sub_url))
videos_l



df_ttl = pd.DataFrame()
for video_num in range(len(videos_l)):
    driver.get(videos_l[video_num])
    time.sleep(10)
    driver.execute_script("window.scrollTo(0, 1080)") 
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 500)") 
    time.sleep(1)
    
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, 'html.parser')

    id_list = soup.select("div#header-author > h3 > #author-text > span")
    comment_list = soup.select("yt-formatted-string#content-text")

    id_final = []
    comment_final = []
    comment_list

    for i in range(len(comment_list)):
        temp_id = id_list[i].text
        temp_id = temp_id.replace('\n', '')
        temp_id = temp_id.replace('\t', '')
        temp_id = temp_id.replace('    ', '')
        id_final.append(temp_id) # 댓글 작성자

        temp_comment = comment_list[i].text
        temp_comment = temp_comment.replace('\n', '')
        temp_comment = temp_comment.replace('\t', '')
        temp_comment = temp_comment.replace('    ', '')
        comment_final.append(temp_comment) # 댓글 내용

    df_ = pd.DataFrame()
    df_['WRITER'] = id_final
    df_['DATETIME'] =(datetime.now() - timedelta(hours=15)).strftime('%Y%m%d-%H%M%S')
    df_['VIEWS'] = np.nan
    df_['LIKES'] = np.nan
    df_['TITLE'] =  comment_final
    df_['CONTENT'] = np.nan

    df_['SOURCE'] = "Youtube_스마트머니"
    df_['RELATED_ITEM'] = np.nan
    df_['POSITIVITY'] = np.nan
#     for i in range(len(df_)):
#         df_.loc[i,"POSITIVITY"] = get_sentiment(df_.loc[i,"TITLE"])

    df_['OTHERS'] = df_[['WRITER']].to_dict('records')
    df_['OTHERS'] = df_['OTHERS'].astype(str)
    df_['NUM_REPLY'] =np.nan
    df_['CRAWLING_DATETIME'] = (datetime.now() ).strftime('%Y%m%d-%H%M%S')
    df_['URL'] =  videos_l[video_num]
    df_
    df_ttl = df_ttl.append(df_)
driver.close()
df_ttl




df_new = df_ttl[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]]
# df_new['YYYYMMDD'] = df_new['DATETIME'] .str[:8]
df_new

df_already = pd.read_sql("SELECT * FROM TABLE_BUZZ where SOURCE = 'Youtube_스마트머니'",conn)
df_already

df_final = pd.DataFrame() 
df_new = df_new[~df_new['URL'].isin(df_already['URL'])].reset_index(drop=True)
df_final = df_final.append(df_new)
df_final
driver.quit()

if len(df_final) >0:

    df_final = df_final.reset_index(drop=True)
    for i in range(len(df_final)):
        df_final.loc[i,"POSITIVITY"] = get_sentiment(df_final.loc[i,"TITLE"])
    df_final
    df_final.to_sql('TABLE_BUZZ',conn,if_exists = 'append',index = False)
    print((datetime.now() ).strftime('%Y%m%d-%H%M%S')  , " Youtube_스마트머니 - SUCCESS  : ",len(df_final))

else:
    print((datetime.now() ).strftime('%Y%m%d-%H%M%S') , " Youtube_스마트머니 - NO DATA TO UPDATE")