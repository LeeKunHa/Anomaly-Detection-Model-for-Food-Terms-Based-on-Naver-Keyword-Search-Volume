#라이브러리
import pandas as pd
import numpy as np
import random
from datetime import datetime
from dateutil.relativedelta import *
from powernad.API.Campaign import *
from powernad.API.RelKwdStat import *
from time import sleep

#자체 파일
from config import *
_cfg = config
import Relative_Value

#프로젝트용
#from Naver_Search_Amount import Relative_Value
#from Naver_Search_Amount.config import *
#_cfg = config

#경고제거
import warnings
warnings.filterwarnings(action='ignore')
#판다스 설정
pd.set_option('display.max_columns', 250)
pd.set_option('display.max_rows', 250)
pd.set_option('display.width', 100)
#소수점 아래 5자리까지 표시
pd.options.display.float_format = '{: .5f}'.format


# 특정 검색어의 한달치 실제 검색량 구하기
# 검색어의 최근 한달 검색량 반환
def search_keyword(searchword):
    #광고API 인증정보
    BASE_URL = _cfg['NAVER_AD']['BASE_URL']
    API_KEY = _cfg['NAVER_AD']['API_KEY']
    SECRET_KEY = _cfg['NAVER_AD']['SECRET_KEY']
    CUSTOMER_ID = _cfg['NAVER_AD']['CUSTOMER_ID']
    
    rel = RelKwdStat(BASE_URL, API_KEY, SECRET_KEY, CUSTOMER_ID)
    kwdDataList = rel.get_rel_kwd_stat_list(siteId=None, biztpId=None, hintKeywords=searchword, event=None, month=None, showDetail='1')
    kwd_result = (kwdDataList[0].relKeyword, #키워드
                 kwdDataList[0].monthlyPcQcCnt, #월간 검색수 (PC)-최근30일
                 kwdDataList[0].monthlyMobileQcCnt, # 월간 검색수 (Mobile)-최근30일
                 kwdDataList[0].monthlyPcQcCnt+kwdDataList[0].monthlyMobileQcCnt) # 월간 total 

    return(kwd_result[3])



# 실제값으로 변환
def real_amount(keyword,df,total_max_key,single_list):
    #결측값이 있는 검색어가 포함되지 않도록(식품안전나라와 같이 결측값이 측정에 들어가면 오차 수치가 낮아짐. 예외처리 해줘야함)
    keyword = [x.replace(' ','') for x in keyword]
    sample_candidate = []
    for i in df.columns: 
        if (df[i].isnull().any() == False):
            sample_candidate.append(i)
    keyword = [x for x in keyword if x not in single_list] #개별로 계산한 single_list로 계산하지 않도록
    keyword = [x for x in keyword if x in sample_candidate]

    #실제값 변환, 오차율,MSE를 구하기 위한 샘플
    keyword_sample = random.sample(keyword, 5) #5개만으로 추출하지만, 예비용으로 10개 설정

    #최근 한달이 이전30일을 제공하기 떄문에 -1month 가 아닌 -30days(오늘 제외)
    start_date = str(datetime.now().date() - relativedelta(days=30)) #한달 전
    end_date =  str(datetime.now().date() - relativedelta(days=1)) #어제

    calculator_dict = {}
    #last_month_index = int(df[df['날짜']==start_date].index.values)
    month_amount_dict = {}
    for i in keyword_sample:
        last_month = df.tail(30)[i] #원래 인덱스로 읽어왔으나, 결측값이 있는 경우 인덱스가 줄어들기 때문에 tail(30)이 정확하다고 판단하여 수정
        month_amount = search_keyword(i) # 검색어 하나의 한달 실제 검색량
        month_amount_dict[i] = month_amount
        calculator = month_amount / last_month.sum() # 100의 값(100값 x 비율(values) 하면 실제 값이 나옴)
        calculator_dict[i] = calculator
        sleep(0.3)

    calculator = sum(calculator_dict.values()) / len(keyword_sample)
    result = df.iloc[:,1:] * calculator
    final_df = pd.concat([df['날짜'], result], axis=1)

    #성능평가(오차율, MSE). 오차를 측정할 경우 일일 호출량이 더 사용된다.
    #print("5개의 샘플을 추출하여 오차율과 MSE를 계산 중 입니다...")
    error_per_list = []
    MSE_list =[]
    for i in calculator_dict.items():
        temp_df = Relative_Value.one_search(i[0])
        real_amount_month = month_amount_dict[i[0]] / temp_df[i[0]].tail(30).sum()
        real_amount_df = real_amount_month * temp_df[i[0]].tail(30)
        error_per = (abs(real_amount_df.mean() - result.tail(30)[i[0]].mean())*100/real_amount_df.mean())
        MSE = np.square(real_amount_df.mean() - result.tail(30)[i[0]].mean()).sum()/len(result)
        error_per_list.append(error_per)
        MSE_list.append(MSE)        
        #print(f"검색어 '{i[0]}'에 대한 오차율: {error_per}, MSE: {MSE}")
        
    #오차율 기준(10%)을 넘는 샘플이 있으면 다시 샘플 추출
    if (len(keyword) >= 50) and (sorted(error_per_list, reverse=True)[0] >= 10): #리스트 내 검색어 수가 50개가 넘을 시에만 실행
        print('오차율 10% 넘는 샘플이 발견되어 샘플을 다시 추출합니다..')
        real_amount(keyword,df,total_max_key,single_list) #재귀함수
    #결측값이 있으면서 total_max_key보다 큰 값은 따로 concat (이상치여도 어쩔 수 없음)
    if len(single_list) > 0:
        for i in single_list:
            single_df = Relative_Value.one_search([total_max_key,i])
            single_amount = search_keyword(i) / single_df[i].tail(30).sum()
            single_amount_df = single_amount * single_df[i]
            final_df = pd.concat([final_df, single_amount_df], axis=1, sort=True)
    return final_df, np.mean(error_per_list), np.mean(MSE_list)