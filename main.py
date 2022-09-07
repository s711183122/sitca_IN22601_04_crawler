#coding:utf-8
from genericpath import isdir
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import datetime
from viewstate import ViewState
from tqdm import tqdm 

def get_years_company(sp):
    com_id =[i['value'] for i in sp.find('select', id='ctl00_ContentPlaceHolder1_ddlQ_Comid').find_all('option')]
    com_YM =[i['value'] for i in sp.find('select', id='ctl00_ContentPlaceHolder1_ddlQ_YM').find_all('option')]
    return com_id, com_YM

def pre_get(url):
    first_response = requests.get(url)
    first_sp = BeautifulSoup(first_response.text, 'lxml')
    return first_sp, first_response

def get_post_data(first_sp, first_response, YM, Comid):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'}
    post_data = {
        "__EVENTTARGET":"",
        "__EVENTARGUMENT":"",
        "__LASTFOCUS":"",
        "__VIEWSTATE":first_sp.find('input', id="__VIEWSTATE")['value'],
        "__VIEWSTATEGENERATOR":first_sp.find('input', id="__VIEWSTATEGENERATOR")['value'],
        "__EVENTVALIDATION":first_sp.find('input', id="__EVENTVALIDATION")['value'],
        "ctl00$ContentPlaceHolder1$ddlQ_YM":YM,
        "ctl00$ContentPlaceHolder1$rdo1":"rbComCL",
        "ctl00$ContentPlaceHolder1$ddlQ_Comid1":Comid,
        "ctl00$ContentPlaceHolder1$ddlQ_Class1":"",
        "ctl00$ContentPlaceHolder1$BtnQuery":"查詢"
    }
    headers['Cookies'] = first_response.headers['Set-Cookie']
    return post_data, headers

def post_(url, post_data, headers):
    response = requests.post(url, headers = headers, data=post_data)
    sp = BeautifulSoup(response.text, 'lxml')
    vs = ViewState(sp.find('input', id="__VIEWSTATE")['value']).decode()[0][1][1][1][1][1][1][3][1][7][0][1]
    return vs

def data(vs, Ym, Comid):
    now = datetime.datetime.now()
    df = pd.read_html(vs, header=0)[0]
    df['更新時間'] = f'{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}'
    df.to_csv(f'./output/{Ym}/{Comid}_{Ym}__{now.year}_{now.month}_{now.day}_{now.hour}_{now.minute}_{now.second}.csv')

def run(url, Ym, Comid):
    fsp, pr = pre_get(url)
    post_data, headers = get_post_data(fsp, pr, Ym, Comid)
    vs = post_(url, post_data, headers)
    data(vs, Ym, Comid)

def main():
    url = 'https://www.sitca.org.tw/ROC/Industry/IN2629.aspx?pid=IN22601_04'
    com_id, com_YM = get_years_company(pre_get(url)[0])
    if not os.path.isdir('./output'):
        os.makedirs('./output')
    for i in com_YM:
        if not os.path.isdir(f'./output/{i}'):
            os.makedirs(f'./output/{i}')
    run_list = []
    [[run_list.append([c_ym,c_id]) for c_id in com_id] for c_ym in com_YM]
    for [ c_ym , c_id ] in tqdm(run_list):
        run(url, c_ym, c_id)



if __name__ == '__main__':
    main()