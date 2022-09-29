import sqlite3 
conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
cur = conn.cursor()

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
    
appid = 1248716281

url = 'https://itunes.apple.com/kr/rss/customerreviews/page=1/id=%i/sortby=mostrecent/xml' % appid
try:
    response = requests.get(url).content.decode('utf8')
    xml = xmltodict.parse(response)
    last_url = [l['@href'] for l in xml['feed']['link'] if (l['@rel'] == 'last')][0]
    last_index = [int(s.replace('page=', '')) for s in last_url.split('/') if ('page=' in s)][0]
    
except Exception as e:
    print (url)
#     print ('\tNo Reviews: appid %i' %appid)
#     print ('\tException:', e)
    
    
result = list()
for idx in range(1, 14+1):
    url = "https://itunes.apple.com/kr/rss/customerreviews/page=%i/id=%i/sortby=mostrecent/xml?urlDesc=/customerreviews/id=%i/sortBy=mostRecent/xml" % (idx, appid, appid)
#     print(url)
    response = requests.get(url).content.decode('utf8')
    try:
        xml = xmltodict.parse(response)
    except Exception as e:
#         print ('\tXml Parse Error %s\n\tSkip %s :' %(e, url))
        continue

    try:
        num_reivews= len(xml['feed']['entry'])
    except Exception as e:
#         print ('\tNo Entry', e)
        continue

    try:
        xml['feed']['entry'][0]['author']['name']
        single_reviews = False
    except:
        #print ('\tOnly 1 review!!!')
        single_reviews = True
        pass

    if single_reviews:
            result.append({
                'USER': xml['feed']['entry']['author']['name'],
                'DATE': xml['feed']['entry']['updated'],
                'STAR': int(xml['feed']['entry']['im:rating']),
                'LIKE': int(xml['feed']['entry']['im:voteSum']),
                'TITLE': xml['feed']['entry']['title'],
                'REVIEW': xml['feed']['entry']['content'][0]['#text'],
            })
    else:
        for i in range(len(xml['feed']['entry'])):
            result.append({
                'USER': xml['feed']['entry'][i]['author']['name'],
                'DATE': xml['feed']['entry'][i]['updated'],
                'STAR': int(xml['feed']['entry'][i]['im:rating']),
                'LIKE': int(xml['feed']['entry'][i]['im:voteSum']),
                'TITLE': xml['feed']['entry'][i]['title'],
                'REVIEW': xml['feed']['entry'][i]['content'][0]['#text'],
            })

df_ = pd.DataFrame(result)
df_

df_['DATETIME'] = df_['DATE'].str.replace("-","").str.replace("T","-").str.replace(":","").str[:15]
df_['VIEWS'] = np.nan
df_['LIKES'] = df_['LIKE']
df_['TITLE'] =  df_['TITLE']
df_['CONTENT'] = df_['REVIEW']
df_['WRITER'] = df_['USER']

df_['SOURCE'] = "Appstore_m.Stock"
df_['RELATED_ITEM'] = "미래에셋증권"
df_['POSITIVITY'] = np.nan
for i in range(len(df_)):
    df_.loc[i,"POSITIVITY"] = get_sentiment(df_.loc[i,"TITLE"])
    
df_['OTHERS'] = df_[['STAR']].to_dict('records')
df_['OTHERS'] = df_['OTHERS'].astype(str)
df_['NUM_REPLY'] = np.nan
df_['CRAWLING_DATETIME'] = (datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')
df_['URL'] =  np.nan
df_ttl = df_[['SOURCE','RELATED_ITEM',"DATETIME","TITLE","CONTENT","POSITIVITY","NUM_REPLY",'URL',"CRAWLING_DATETIME","OTHERS"]]
df_ttl

df_already= pd.read_sql("SELECT * FROM TABLE_BUZZ where SOURCE  = 'Appstore_m.Stock' ORDER BY DATETIME desc",conn)
df_already

df_ttl = df_ttl[df_ttl['DATETIME'] > df_already['DATETIME'].max()].reset_index(drop=True)


if len(df_ttl) >0:

    df_ttl = df_ttl.reset_index(drop=True)

    df_ttl
    df_ttl.to_sql('TABLE_BUZZ',conn,if_exists = 'append',index = False)
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S')  , " m.Stock //  SUCCESS  : ",len(df_ttl))

else:
    print((datetime.now() + timedelta(hours=9)).strftime('%Y%m%d-%H%M%S') , "  m.Stock //  NO DATA TO UPDATE")
