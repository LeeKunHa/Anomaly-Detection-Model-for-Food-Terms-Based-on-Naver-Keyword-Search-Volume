# 라이브러리
import pandas as pd
# 자체 파일
from Anomaly_Detection import *

df = pd.read_csv('../Naver_Search_Amount/data/result/search_result_absolute20230213.csv', encoding='cp949')
df['날짜'] = df['날짜'].astype('datetime64[ns]')
# 시계열 그래프 작성을 위해 값이 2개 최소 이상인 검색어만 추출
df_ = df[df.columns[df.isnull().sum() < len(df)-1]]
df_ = df_.iloc[:,:20] # 필요시 개수 제한
df_anomaly = Anomaly_Detect(df_)
df_anomaly.to_csv('data/Anomaly_result.csv', encoding='cp949', index=False)
df_anomaly_yes, df_anomaly_low = Extract_date(df_anomaly,df_)
df = key_keyword(df_anomaly_yes)
df.to_csv('data/anomaly_keyword.csv', encoding='cp949', index=False, header=False)
