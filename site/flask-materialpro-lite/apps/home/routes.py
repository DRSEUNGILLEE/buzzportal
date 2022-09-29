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


@blueprint.route('/index')
@login_required
def index():
    conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
    cur = conn.cursor()
    
    today_date = datetime.today().strftime('%Y%m%d')
    prev_date = (datetime.today() - relativedelta(months=3)).strftime('%Y%m%d')
    
    if request.method == 'GET':
        df_temp = pd.read_sql(f"SELECT * FROM TABLE_APPKPI WHERE ((NAME like '%m.%') OR (NAME like '%M-ST%')) AND YYYYMMDD BETWEEN '{prev_date}' AND '{today_date}' AND DATA_TYPE = '사용자수'",conn)
        
        df_temp.index = pd.to_datetime(df_temp.loc[:, 'YYYYMMDD'])
        df_temp.VALUE = df_temp.VALUE.astype(int)
        df_final = df_temp.groupby('NAME').resample('W').sum().reset_index()
        result = df_final.loc[df_final.NAME == '미래에셋증권 M-STOCK']
        result.YYYYMMDD = result.YYYYMMDD.astype(str)
#         result.VALUE = result.VALUE.astype(int)
#         result.YYYYMMDD = pd.to_datetime(result.loc[:, 'YYYYMMDD']).dt.date
        
        return render_template('home/index.html', x_axis=list(result.YYYYMMDD.values), y_axis=result.VALUE.values.tolist(), results = result, columns=df_final.NAME.unique())
    
    elif request.method == 'POST':
        search_keyword = request.form['key_word']
        menu_panel = request.form['menu']
        df_feeds= pd.read_sql(f"""
        SELECT * 
        FROM TABLE_BUZZ 
        WHERE TITLE LIKE '%{search_keyword}%'
        ORDER BY DATETIME 
        LIMIT 10
        """, conn)
        
        return render_template('home/index.html')
# , segment='index'


# @blueprint.route('/table-basic')
# @login_required
# def tablebasic():

#     return render_template('home/table-basic.html')


@blueprint.route('/feeds', methods=('GET', 'POST'))
@login_required
def feeds_main():
    conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
    cur = conn.cursor()
    
    if request.method == 'GET':
        df_feeds= pd.read_sql("""SELECT * FROM TABLE_BUZZ ORDER BY DATETIME DESC LIMIT 10""", conn)

        return render_template('home/feeds.html', column_names=df_feeds.columns.values, row_data=list(df_feeds.values.tolist()))
    
    elif request.method == 'POST':
        search_keyword = request.form['key_word']
        menu_panel = request.form['menu']
        df_feeds= pd.read_sql(f"""
        SELECT * 
        FROM TABLE_BUZZ 
        WHERE TITLE LIKE '%{search_keyword}%'
        ORDER BY DATETIME 
        LIMIT 10
        """, conn)


    return render_template('home/feeds.html', column_names=df_feeds.columns.values, row_data=list(df_feeds.values.tolist()), search_keyword=search_keyword)


@blueprint.route('/feeds/<tab>')
def feeds_tab(tab):
    conn = sqlite3.connect("/home/lsi8505/miraeasset/crawling/opinion_outside.db")
    cur = conn.cursor()

    if tab == "google":
        condition = "구글뉴스"
        
    elif tab == "blind":
        condition = "블라인드_주식투자"
        
    elif tab == "appstore":
        condition = "Appstore_m.Stock"
        
    elif tab == "해외주식갤러리":
        condition = "dcinside_해외주식갤러리"

    elif tab == "미국주식갤러리":
        condition = "dcinside_미국주식갤러리"
        
    elif tab == "naver":
        condition = "네이버_종목토론실"
        
    else:
        pass
    df_feeds= pd.read_sql(f"""
                          SELECT * 
                          FROM TABLE_BUZZ 
                          WHERE SOURCE = '{condition}'
                          ORDER BY DATETIME 
                          LIMIT 10
                            """, conn)
    
    return render_template('home/feeds.html', column_names=df_feeds.columns.values, row_data=list(df_feeds.values.tolist()))