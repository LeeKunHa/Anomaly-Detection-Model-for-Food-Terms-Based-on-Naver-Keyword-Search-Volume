import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import urllib.request
import json
import glob
import sys
import os
import hashlib
import hmac
import base64
import random

from tqdm.notebook import tqdm
from datetime import datetime
from pandas.io.json import json_normalize
from prophet import Prophet
from dateutil.relativedelta import *

import warnings
warnings.filterwarnings(action='ignore')

pd.set_option('display.max_columns', 250)
pd.set_option('display.max_rows', 250)
pd.set_option('display.width', 100)
#소수점 아래 5자리까지 표시
pd.options.display.float_format = '{: .5f}'.format

class Parameter():
    def __init__(self):
        self.num = random.randrange(len(_cfg['NAVER_TREND'].items())/2) #생성한 api 수 만큼 설정(0~-1까지이므로 개수와 동일)
        # 검색어 지정
        #keyword = keyword_list##################
        self.client_id = _cfg['NAVER_TREND'][f'client_id{self.num}']
        self.client_secret = _cfg['NAVER_TREND'][f'client_secret{self.num}']
    # 광고API 인증정보
    BASE_URL = _cfg['NAVER_AD']['BASE_URL']
    API_KEY = _cfg['NAVER_AD']['API_KEY']
    SECRET_KEY = _cfg['NAVER_AD']['SECRET_KEY']
    CUSTOMER_ID = _cfg['NAVER_AD']['CUSTOMER_ID']
    
    # 요청 파라미터 설정
    """
    요청 결과 반환
    timeUnit - 'date', 'week', 'month'
    device - None, 'pc', 'mo'
    ages = [], ['1' ~ '11']
    gender = None, 'm', 'f'
    """
    startDate = str(datetime(2016, 1, 1).strftime('%Y-%m-%d')) #네이버API 최초 제공일자
    endDate = str(datetime.now().date().strftime('%Y-%m-%d')) #오늘
    timeUnit = 'date'
    device = ''
    ages = []
    gender = ''

class NaverDataLabOpenAPI():
    """
    네이버 데이터랩 오픈 API 컨트롤러 클래스
    """
    
    def __init__(self):
        """
        인증키 설정 및 검색어 그룹 초기화
        """
        parameter_ = Parameter()
        self.client_id = parameter_.client_id
        self.client_secret = parameter_.client_secret
        self.keywordGroups = []
        self.url = "https://openapi.naver.com/v1/datalab/search"

    def add_keyword_groups(self, group_dict):
        """
        검색어 그룹 추가
        """

        keyword_gorup = {
            'groupName': group_dict['groupName'],
            'keywords': group_dict['keywords']
        }
        
        self.keywordGroups.append(keyword_gorup)
        #print(f">>> Num of keywordGroups: {len(self.keywordGroups)}")
        
    def get_data(self):
        # Request body
        body = json.dumps({
            "startDate": Parameter.startDate,
            "endDate": Parameter.endDate,
            "timeUnit": Parameter.timeUnit,
            "keywordGroups": self.keywordGroups,
            "device": Parameter.device,
            "ages": Parameter.ages,
            "gender": Parameter.gender
        }, ensure_ascii=False)
        
        # Results
        request = urllib.request.Request(self.url)
        request.add_header("X-Naver-Client-Id",self.client_id)
        request.add_header("X-Naver-Client-Secret",self.client_secret)
        request.add_header("Content-Type","application/json")
        response = urllib.request.urlopen(request, data=body.encode("utf-8"))
        rescode = response.getcode()
        if(rescode==200):
            # Json Result
            result = json.loads(response.read())
            
            df = pd.DataFrame(result['results'][0]['data'])[['period']]
            for i in range(len(self.keywordGroups)):
                tmp = pd.DataFrame(result['results'][i]['data'])
                tmp = tmp.rename(columns={'ratio': result['results'][i]['title']})
                df = pd.merge(df, tmp, how='left', on=['period'])
            self.df = df.rename(columns={'period': '날짜'})
            self.df['날짜'] = pd.to_datetime(self.df['날짜'])
            
        else:
            print("Error Code:" + rescode)
            
        return self.df

