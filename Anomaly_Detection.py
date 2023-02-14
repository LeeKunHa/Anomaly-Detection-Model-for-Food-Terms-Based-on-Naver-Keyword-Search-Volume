import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from tqdm.notebook import tqdm
from prophet import Prophet
from dateutil.relativedelta import relativedelta

def Anomaly_Detect(df):
    final_df = df.copy()
    final_df['날짜'] = final_df['날짜'].astype('datetime64[ns]')
    df_anomaly = final_df[['날짜']]
    weight = 1.5

    final_df = final_df[final_df.columns[final_df.apply(lambda x: len(x[x.notnull().values]) > 30).values == True]] # 값이 30개 이상인 항목만
    for search_key in tqdm(final_df.columns[1:]): #'날짜'제외
        new_df = final_df[['날짜', search_key]]
        new_df = new_df.set_index('날짜')
        new_df_prophet = new_df.reset_index()[['날짜', new_df.columns[0]]].rename({'날짜':'ds', new_df.columns[0]:'y'}, axis='columns')
        m = Prophet()#changepoint_range=0.95, changepoint_prior_scale=0.05) #holidays=holidays)
        m.add_country_holidays(country_name='KR')
        m.fit(new_df_prophet)
        future = m.make_future_dataframe(periods=365, freq='D')
        forecast = m.predict(future)
        #new_df_prophet['ds'] = new_df_prophet['ds'].astype('datetime64[ns]')
        result = pd.concat([new_df_prophet.set_index('ds')['y'], forecast.set_index('ds')[['yhat','yhat_lower','yhat_upper']]], axis=1)
        result['error'] = result['y'] - result['yhat'] #실제값 - 예측값범위
        result['uncertainty'] = result['yhat_upper'] - result['yhat_lower'] #범위, 불확실성
        # 본래 abs를 붙여 낮게 나온 이상치도 출력하는 코드였지만, 검색어 특성상 높게 나온 지점만 산출하기 위해 abs 삭제
        #비율에 따라, 검색량이 절대적으로 적은(일정 수치 이하) 경우는 가중치를 바꾸도록??
        result['anomaly'] = result.apply(lambda x: 'Yes' if((x['error']) > weight*x['uncertainty']) else 'No', axis = 1) #원래는 1.5. 나는 0.4
        result['anomaly'] = result.apply(lambda x: 'Low' if (x['anomaly']=='Yes') & (x['y'] < 10000) else 'Yes' if (x['anomaly']=='Yes') & (x['y'] >= 1000) else 'No', axis=1) #1000 이하는 Low로
        result = result.fillna(0)
        result['label'] = [[x[0],x[-1]] for x in result.values] # 컬럼에 y,anomaly 할당
        #result_new = result[result['anomaly']=='Yes']
        #anomaly_list = list(result_new.index)
        df_temp = result['label'].reset_index().rename(columns={'ds':'날짜','label':search_key})
        df_anomaly = pd.merge(df_anomaly,df_temp, on = '날짜')
    return df_anomaly

def Extract_date(df_anomaly,df_raw):
    anomaly_list = []
    low_list = []
    for i in range(len(df_anomaly)):
        if 'Yes' in [x[1] for x in df_anomaly.iloc[:,1:].values[i]]:
            #print(sum(df_anomaly.iloc[:,1:].values[i]))
            anomaly_list.append(df_raw['날짜'][i])
        elif 'Low' in [x[1] for x in df_anomaly.iloc[:,1:].values[i]]:
            low_list.append(df_raw['날짜'][i])

    anomaly_list = pd.DataFrame(anomaly_list, columns=['날짜'])
    df_anomaly_yes = pd.merge(anomaly_list, df_anomaly, how='inner', on='날짜')
    df_anomaly_yes['날짜'] = df_anomaly_yes['날짜'].astype('string')
    df_anomaly_yes = df_anomaly_yes.set_index('날짜')

    low_list = pd.DataFrame(low_list, columns=['날짜'])
    df_anomaly_low = pd.merge(low_list, df_anomaly, how='inner', on='날짜')
    df_anomaly_low['날짜'] = df_anomaly_low['날짜'].astype('string')
    df_anomaly_low = df_anomaly_low.set_index('날짜')
    return df_anomaly_yes, df_anomaly_low


def key_keyword(df_anomaly_yes):
    # 검색어별로 보기
    df_anomaly_dict = {}
    for i in range(len(df_anomaly_yes.columns)):
        temp_list = []
        for j in range(len(df_anomaly_yes.iloc[:,i])):
            if df_anomaly_yes.iloc[j][i][1] == 'Yes':
                temp_list.append(df_anomaly_yes.index[j])
                #print(df_anomaly_yes.index[i],df_anomaly_yes.columns[j])
            df_anomaly_dict[df_anomaly_yes.columns[i]] = temp_list
    return pd.DataFrame(df_anomaly_dict.items(), columns=['검색어','날짜'])


def key_date(df_anomaly_yes):
    # 날짜 별로 보기(어제 날짜 뽑을 때 사용)
    df_anomaly_dict = {}
    for i in range(len(df_anomaly_yes)):
        temp_list = []
        for j in range(len(df_anomaly_yes.iloc[i])):
            if df_anomaly_yes.iloc[i][j][1] == 'Yes':
                temp_list.append(df_anomaly_yes.columns[j])
                #print(df_anomaly_yes.index[i],df_anomaly_yes.columns[j])
            df_anomaly_dict[df_anomaly_yes.index[i]] = temp_list
    return pd.DataFrame(df_anomaly_dict.items(), columns=['날짜','검색어'])
    