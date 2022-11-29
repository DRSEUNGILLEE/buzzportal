# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps.home import blueprint
from flask import render_template, request
from flask_login import login_required
from jinja2 import TemplateNotFound
from datetime import datetime, timedelta
from dateutil.relativedelta import *
import sqlite3
import pandas as pd
import numpy as np
from flask import json
from flask import jsonify

feed_N = 20


@blueprint.route('/index')
@login_required
def index():
    conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
    cur = conn.cursor()
    
    today_date = datetime.today().strftime('%Y%m%d')
    prev_date = (datetime.today() - relativedelta(months=3)).strftime('%Y%m%d')
    

    df_ttl = pd.read_sql("SELECT count(*) FROM TABLE_BUZZ",conn)
    df_ttl
    
    ymd = datetime.now().strftime("%Y%m%d")
    df_today = pd.read_sql(f"SELECT count(*) FROM TABLE_BUZZ WHERE DATETIME LIKE '{ymd}%'" ,conn)
    df_today.iloc[0,0]
#         df_temp.index = pd.to_datetime(df_temp.loc[:, 'YYYYMMDD'])
#         df_temp.VALUE = df_temp.VALUE.astype(int)
#         df_final = df_temp.groupby('NAME').resample('W').sum().reset_index()
#         result = df_final.loc[df_final.NAME == '미래에셋증권 M-STOCK']
#         result.YYYYMMDD = result.YYYYMMDD.astype(str)
#         result.VALUE = result.VALUE.astype(int)
#         result.YYYYMMDD = pd.to_datetime(result.loc[:, 'YYYYMMDD']).dt.date

    today_cnt = df_today.iloc[0,0]
    ttl_cnt = df_ttl.iloc[0,0]

    return render_template('home/index.html', today_cnt = today_cnt,ttl_cnt = ttl_cnt)



@blueprint.route('/feeds', methods=('GET', 'POST'))
@login_required
def feeds_main():
    conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
    cur = conn.cursor()
#     if len (request.form) ==0:
#         1==1
#         search_keyword = ""
#     else:
#         search_keyword = request.form['search_keyword']

#     menu_panel = request.args.get('menu',"")
        
        
    if request.method == 'GET':
        search_keyword = ""
    elif request.method == 'POST':
        print("posted" * 10)
        search_keyword = request.form['search_keyword']
        print(search_keyword)

    

#     df_feeds= pd.read_sql(f"""
#                         SELECT
#                         * 
#                         FROM TABLE_BUZZ 
#                         WHERE TITLE LIKE '%{search_keyword}%'
#                         ORDER BY DATETIME  desc
#                         LIMIT  {feed_N * 1/2}
#     """, conn)
    df_feeds_app= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'App%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)}
                        """, conn)
    
    df_feeds_play= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Playstore%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)} 
                        """, conn)
        
 
    df_feeds_youtube= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Youtube%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)}
                        """, conn)
    df_feeds_naver= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '네이버%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.15)}
                        """, conn)
    df_feeds_news= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%뉴스%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.15)}
                        """, conn)
    df_feeds_dcinside= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%dcinside%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)}
                        """, conn)
    df_feeds_blind= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%블라인드%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)}
                        """, conn)

    df_feeds = df_feeds_blind.append(df_feeds_dcinside).append(df_feeds_news).append(df_feeds_naver).append(df_feeds_youtube).append(df_feeds_app).append(df_feeds_play)
    df_feeds = df_feeds.sample(len(df_feeds))
    df_feeds = df_feeds[~df_feeds['TITLE'].duplicated()].reset_index(drop=True)
    
        
    df_feeds['POSITIVITY'] = df_feeds['POSITIVITY'].fillna(0).apply(lambda x: np.round(x,1))

    return render_template('home/feeds.html', column_names=df_feeds.columns.values, row_data=list(df_feeds.values.tolist()), search_keyword_word=search_keyword, main_YN = "Y")


@blueprint.route('/feeds/<tab>', methods=('GET', 'POST'))
def feeds_tab(tab):
    conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
    cur = conn.cursor()

        
    if request.method == 'GET':
        search_keyword = ""
    elif request.method == 'POST':
        print("posted" * 10)
        search_keyword = request.form['search_keyword']
        print(search_keyword)

    if tab == "뉴스":
        condition = "%뉴스"
        
    elif tab == "blind":
        condition = "블라인드_%"
        
    elif tab == "appstore":
        condition = "Appstore_%"
    elif tab == "Playstore":
        condition = "Playstore_%"
        
    elif tab == "dcinside투자게시판":
        condition = "dcinside_%"
       
    elif tab == "네이버종목토론실":
        condition = "네이버_종목토론실"
    elif tab == "유튜브":
        condition = "Youtube_%"
                
    else:
        pass
    df_feeds= pd.read_sql(f"""
                          SELECT * 
                          FROM TABLE_BUZZ 
                          WHERE  TITLE LIKE '%{search_keyword}%'  and SOURCE like '{condition}'
                          ORDER BY DATETIME  desc
                           LIMIT {feed_N *2} 
                            """, conn)
    df_feeds = df_feeds[~df_feeds['TITLE'].duplicated()].reset_index(drop=True)
    df_feeds['POSITIVITY'] = df_feeds['POSITIVITY'].fillna(0).apply(lambda x: np.round(x,1))
#     df_feeds['RELATED_ITEM'] = df_feeds['RELATED_ITEM'].fillna("")
    
    return render_template('home/feeds.html', column_names=df_feeds.columns.values, row_data=list(df_feeds.values.tolist()) , main_YN = "N", tab = tab, search_keyword_word=search_keyword,)


@blueprint.route('/feeds_request/<num>/<search_keyword>/<data_source>')
def feeds_request(num,search_keyword,data_source):
    conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
    cur = conn.cursor()
    print("???"*10,search_keyword)
    if search_keyword == "''":
        print("oo"*10,search_keyword)
        search_keyword = ""
    else:
        print("oo"*10,search_keyword)
        search_keyword = search_keyword.replace("'","")
    num = float(num)
    df_feeds_app= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'App%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)} OFFSET {np.round(feed_N * 0.1)*num}
                        """, conn)
    df_feeds_play= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Playstore%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)} 
                        """, conn)
        
 

    df_feeds_play= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Playstore%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)} OFFSET {np.round(feed_N * 0.1)*num}
                        """, conn)
    
    df_feeds_youtube= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Youtube%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)} OFFSET {np.round(feed_N * 0.2)*num}
                        """, conn)
    df_feeds_naver= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '네이버%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.15)} OFFSET {np.round(feed_N * 0.15)*num}
                        """, conn)
    df_feeds_news= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%뉴스%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.15)} OFFSET {np.round(feed_N * 0.15)*num}
                        """, conn)
    df_feeds_dcinside= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%dcinside%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)} OFFSET {np.round(feed_N * 0.2)*num}
                        """, conn)
    df_feeds_blind= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%블라인드%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)} OFFSET {np.round(feed_N * 0.2)*num}
                        """, conn)

    if data_source  == "undefined":  
#         print("z"*100)

        df_feeds = df_feeds_blind.append(df_feeds_dcinside).append(df_feeds_news).append(df_feeds_naver).append(df_feeds_youtube).append(df_feeds_app).append(df_feeds_play)
    elif data_source  == "유튜브": 
         df_feeds = df_feeds_youtube.copy()
    elif data_source  == "appstore": 
         df_feeds = df_feeds_app.copy()       
    elif data_source  == "Playstore": 
         df_feeds = df_feeds_play.copy()       
    elif data_source  == "dcinside투자게시판": 
         df_feeds = df_feeds_dcinside.copy()       
    elif data_source  == "blind": 
         df_feeds = df_feeds_blind.copy()       
    elif data_source  == "뉴스": 
         df_feeds = df_feeds_news.copy()       
    elif data_source  == "네이버종목토론실": 
         df_feeds = df_feeds_naver.copy()               
        
    df_feeds = df_feeds.sample(len(df_feeds))
    df_feeds = df_feeds[~df_feeds['TITLE'].duplicated()].reset_index(drop=True)
    df_feeds['POSITIVITY'] = df_feeds['POSITIVITY'].fillna(0).apply(lambda x: np.round(x,1))
#     print(num,"aaa"*5,len(df_feeds_app),"aaa"*5,len(df_feeds))

    html_send = ""
    for rows in range(len(df_feeds)):
  
        row_type = df_feeds.loc[rows,'SOURCE']
    
        if "블라인드" in  row_type:
             row_image = "blind.JPG"
        elif "Appstore" in  row_type:
            row_image = "appstore.JPG"
        elif "네이버" in  row_type:
            row_image = "naver.JPG"
        elif "dcinside" in  row_type :
            row_image = "dcinside.JPG"
        elif "Youtube" in  row_type :
            row_image = "youtube.JPG"            
        elif "뉴스" in  row_type :  
            row_image = "news.JPG"                     


        row_title = df_feeds.loc[rows,'TITLE']
        link_url = df_feeds.loc[rows,'URL']
        row_item = df_feeds.loc[rows,'RELATED_ITEM']
        positivity = df_feeds.loc[rows,'POSITIVITY']
        html_template = f""" \
                         <div class="profiletimeline border-start-0" style="border:0px solid gold; margin: 10px 10px 0px 10px; padding: 0px 10px 0px 0px;">\
                        \
                        \
                        \
                    <div class="sl-left"  style="margin: 10px 10px 0px 10px; padding: 0px 0px 0px 0px; "> \
                     <img src="/static/assets/images/users/{row_image}" alt="user"     class="img-circle">  \
                    </div>\
                        \
                    \
                        <div class="sl-right"  style="border:0px solid gold;" >\
                        <div><div><a href="#" class="link" style="border:px solid gold; margin: 0px 0px 0px 15px;">{row_type}</a> \
                        <span class="sl-date"> 작성일 :  2022년 10월   26일  15시  13분</span>\
                        <div style="border:0px solid black; margin: 0px 0px 0px 15px; padding: 0px 0px 0px 15px;">\
                     <b>&nbsp; &nbsp;&nbsp; &nbsp; {row_title} &nbsp; &nbsp; </b> \
                     &nbsp; &nbsp;   <a href={link_url} class="link" style="color:blue" target="_blank"> [원문보기]  </a>  <div>\
                     &nbsp; &nbsp;  &nbsp; &nbsp; &nbsp; &nbsp; <span class="sl-date">관련 종목:  {row_item} / </span>  \
                    <span class="sl-date"> 긍정도: {positivity} % </span>\
                    </div>  \
                          \
                        </div> \
                            </div> \
                                </div> \
                                    </div> \
                                     </div> \
                     <hr>\
                     """
        html_send += html_template
    data = {"add_data" : html_send}

 

    return jsonify(data)

@blueprint.route('/KPIs')
@login_required
def KPIs():
    conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
    cur = conn.cursor()
    
    today_date = datetime.today().strftime('%Y%m%d')
    prev_date = (datetime.today() - relativedelta(months=3)).strftime('%Y%m%d')
    
    df_kpi = pd.read_pickle("/home/buzzportal/crawling/dau_ttl.pickle").iloc[:30]
    df_kpi

        
    return render_template("home/KPIs.html" , column_names=df_kpi.columns.values, row_data=list(df_kpi.values.tolist()) )


@blueprint.route('/VOCs')
@login_required
def VOCs():
    conn = sqlite3.connect("/home/buzzportal/crawling/opinion_outside.db")
    cur = conn.cursor()
    
    search_keyword = ""
    data_source  = "undefined"    
    today_date = datetime.today().strftime('%Y%m%d')
    prev_date = (datetime.today() - relativedelta(months=3)).strftime('%Y%m%d')
    num = 1

    df_ttl = pd.read_sql("SELECT count(*) FROM TABLE_BUZZ WHERE RELATED_ITEM = '미래에셋증권'",conn)
    df_ttl
    
    ymd = datetime.now().strftime("%Y%m%d")
    df_today = pd.read_sql(f"SELECT count(*) FROM TABLE_BUZZ WHERE DATETIME LIKE '{ymd}%' and RELATED_ITEM = '미래에셋증권'" ,conn)
    df_today.iloc[0,0]

    df_feeds_app= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'App%'   and RELATED_ITEM = '미래에셋증권'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)} OFFSET {np.round(feed_N * 0.1)*num}
                        """, conn)
    df_feeds_play= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Playstore%'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.1)} 
                        """, conn)
        
 
    df_feeds_youtube= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE 'Youtube%'   and RELATED_ITEM = '미래에셋증권'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)} OFFSET {np.round(feed_N * 0.2)*num}
                        """, conn)
    df_feeds_naver= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '네이버%'   and RELATED_ITEM = '미래에셋증권'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.15)} OFFSET {np.round(feed_N * 0.15)*num}
                        """, conn)
    df_feeds_news= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%뉴스%'   and RELATED_ITEM = '미래에셋증권'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.15)} OFFSET {np.round(feed_N * 0.15)*num}
                        """, conn)
    df_feeds_dcinside= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%dcinside%'   and RELATED_ITEM = '미래에셋증권'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)} OFFSET {np.round(feed_N * 0.2)*num}
                        """, conn)
    df_feeds_blind= pd.read_sql(f"""
                        SELECT
                            * 
                        FROM TABLE_BUZZ 
                        WHERE TITLE LIKE '%{search_keyword}%' and SOURCE LIKE '%블라인드%'   and RELATED_ITEM = '미래에셋증권'
                        ORDER BY DATETIME  desc
                        LIMIT  {np.round(feed_N * 0.2)} OFFSET {np.round(feed_N * 0.2)*num}
                        """, conn)

    if data_source  == "undefined":  
        df_feeds = df_feeds_blind.append(df_feeds_dcinside).append(df_feeds_news).append(df_feeds_naver).append(df_feeds_youtube).append(df_feeds_app).append(df_feeds_play)
    elif data_source  == "유튜브": 
         df_feeds = df_feeds_youtube.copy()
    elif data_source  == "appstore": 
         df_feeds = df_feeds_app.copy()       
    elif data_source  == "dcinside투자게시판": 
         df_feeds = df_feeds_dcinside.copy()       
    elif data_source  == "blind": 
         df_feeds = df_feeds_blind.copy()       
    elif data_source  == "뉴스": 
         df_feeds = df_feeds_news.copy()       
    elif data_source  == "네이버종목토론실": 
         df_feeds = df_feeds_naver.copy()               
        
    df_feeds = df_feeds.sample(len(df_feeds))
    df_feeds = df_feeds[~df_feeds['TITLE'].duplicated()].reset_index(drop=True)
    df_feeds['POSITIVITY'] = df_feeds['POSITIVITY'].fillna(0).apply(lambda x: np.round(x,1))    
    
    
    
    today_cnt = df_today.iloc[0,0]
    ttl_cnt = df_ttl.iloc[0,0]

        
    return render_template("home/VOCs.html" , today_cnt = today_cnt,ttl_cnt = ttl_cnt ,row_data=list(df_feeds.values.tolist()),  column_names=df_feeds.columns.values,  )
