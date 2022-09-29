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
options.add_argument('--disable-dev-shm-usage')
options.add_argument('user-agent={0}'.format(user_agent))
# options =  webdriver.Chrome('/home/porter/NOTEBOOK/chromedriver',options=options)
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
    
    
    

CNT = 15
cnt = CNT

url = "https://www.teamblind.com/kr/topics/주식·투자"
driver = webdriver.Chrome('/home/lsi8505/chromedriver',options=options)
driver.get(url)

while cnt:
#         print(cnt)
    driver.find_element(By.TAG_NAME,'body').send_keys(Keys.PAGE_DOWN)

#     driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
    cnt -= 1

bs_obj = BeautifulStoneSoup(driver.page_source)
div = bs_obj.find('div', {'class': 'article-list '})
posts = div.find_all('div', {'class' : 'tit'})
posts_title = []
for t in posts:
    try:
        posts_title.append(t.find('a').find('span').decompose().text.strip())
    except:
        posts_title.append(t.find('a').text.strip())
posts_href = []
for l in posts:
    tmp = l.find('a')['href']
    posts_href.append(tmp[tmp.rfind('-'):])
posts_title = [re.sub(r'[~()%":\'/,!?]', '', i).replace(' ', '-').replace('\n', '') for i in posts_title]

root_path = "https://www.teamblind.com/kr/post/"
list_url = list()
list_url2 = list()
cnt = 0
#     print('처리 들어간다')

## 크롤링
for title, link in zip(posts_title, posts_href):
    # cnt += 1
    title2 = re.sub('[.]', '', title)
    list_url.append(root_path + title + link)
    list_url2.append(root_path + title2 + link)
url_dirs = pd.DataFrame({'url_raw' : list_url, 'url' : list_url2})
#     url_dirs.to_csv('urls.csv')
data = []
for i in range(len(url_dirs)):
#     print(i ," // ", len(url_dirs), "// ", url_dirs.loc[i,'url'] )
    headers = {'User-Agent': 'Mozilla/5.0'} 
    response = requests.get(url_dirs.loc[i,'url'],  headers=headers)
    response

    bs_obj = BeautifulSoup(response.text)
    title = bs_obj.find('div', {'class' : 'article-view-head'})
    main = bs_obj.find('div', {'class' : 'article-view-contents'})
    like = bs_obj.find('div', {'class' : 'article_info'})
    comment = bs_obj.find('div', {'class' : 'article-comments'})
    try:
        ti = title.find('h2').text # 제목
        da = title.find('span', {'class' : 'date'}).text.replace('작성일', '') # 날짜
        if '일' in da:
            tmp = int(da.replace('일', ''))
            da = (datetime.datetime.today().date() - datetime.timedelta(days = tmp)).strftime('%Y%m%d')
        elif '어제' in da:
            da = (datetime.datetime.today().date() - datetime.timedelta(days = 1)).strftime('%Y%m%d')
        elif '분' in da:
            da = (datetime.datetime.today().date() - datetime.timedelta(days = 0)).strftime('%Y%m%d')
        elif '시간' in da:
            da = (datetime.datetime.today().date() - datetime.timedelta(days = 0)).strftime('%Y%m%d')
        elif '초' in da:
            da = (datetime.datetime.today().date() - datetime.timedelta(days = 0)).strftime('%Y%m%d')

        lo = title.find('span', {'class' : 'pv'}).text.replace('조회수', '') # 조회수

        tmp = main.find('p', {'class' : 'contents-txt'}).text # 본문
        try:
            tmp = tmp[:tmp.index('  ')]
        except:
            pass
        tmp

        try:
            li = like.find('a', {'class' : 'like'}).text.replace('좋아요', '') # 좋아요 수
            if not li:
                li = 0
        except:
            li = 0

        cc = comment.find('h3').text.replace('댓글 ', '') # 댓글 갯수

        if '0' == cc: # 댓글
            co = 0
        else:
            co = ''
            for c in comment.find_all('p', {'class' : 'cmt-txt'}):
                c = c.text
                try:
                    co += (c[:c.index('작성일')] + '\n')
                except:
                    co += (c + '\n')

        dict_data = {'date':da, 'title' : ti, 'main' : tmp, 'comments' : co, 'looks_count' : lo, 'likes_count' : li, 'comments_count' : cc}
    #     print(dict_data)
        data.append(dict_data)

    except:
        print("SPECIAL CHARACTER IN TITLE")    
    time.sleep(0.5)

    
df_ = pd.DataFrame(data).iloc[2:].reset_index(drop=True)

df_['DATETIME'] = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')
df_['VIEWS'] = df_['looks_count']
df_['LIKES'] = df_['likes_count']
df_['TITLE'] =  df_['title']
df_['CONTENT'] = df_['main']
df_['WRITER'] = np.nan

df_['SOURCE'] = "블라인드_주식투자"
df_['RELATED_ITEM'] = np.nan
df_['POSITIVITY'] = np.nan
for i in range(len(df_)):
    df_.loc[i,"POSITIVITY"] = get_sentiment(df_.loc[i,"TITLE"])
    
df_['OTHERS'] = df_[['comments_count']].to_dict('records')
df_['OTHERS'] = df_['OTHERS'].astype(str)
df_['NUM_REPLY'] = np.nan
df_['CRAWLING_DATETIME'] = (datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')
df_['URL'] =  np.nan
df_ = df_[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]]
df_

df_new = df_[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]]
df_new['YYYYMMDD'] = df_new['DATETIME'] .str[:8]
df_new

## 기존 DF에서 겹치는꺼 빼야하니 기존꺼ㅏ 불러오기

df_already = pd.read_sql("SELECT * FROM TABLE_BUZZ where SOURCE = '블라인드_주식투자'",conn)
df_already
df_already['YYYYMMDD'] = df_already['DATETIME'] .str[:8]

df_ttl = df_new[~df_new.index .isin(df_new.merge(df_already, on=['YYYYMMDD','TITLE']).index)]
df_ttl = df_ttl.drop(['YYYYMMDD'],axis=1)
df_ttl

if len(df_ttl) >0:
    df_ttl = df_ttl.reset_index(drop=True)

    df_ttl.to_sql('TABLE_BUZZ',conn,if_exists = 'append',index = False)
    print((datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , " SUCCESS  : ",len(df_ttl))

else:
    print((datetime.datetime.now() + datetime.timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , " NO DATA TO UPDATE")
