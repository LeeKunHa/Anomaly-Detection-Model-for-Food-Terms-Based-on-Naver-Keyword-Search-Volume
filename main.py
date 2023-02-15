# 라이브러리
import pandas as pd
import glob
from natsort import natsorted
# 자체 파일
from Anomaly_Detection import *
from Kakao_send_me import *

def main():
    files = glob.glob('../Naver_Search_Amount/data/result/search_result_absolute*.csv') #최신파일 읽어오기(폴더 경로 입력으로 바꾸기)
    recent_file = natsorted(seq=files, reverse=True)[0]
    df = pd.read_csv(recent_file, encoding='cp949')
    df['날짜'] = df['날짜'].astype('datetime64[ns]')
    # 시계열 그래프 작성을 위해 값이 2개 최소 이상인 검색어만 추출
    df_ = df[df.columns[df.isnull().sum() < len(df)-1]]
    #df_ = df_.iloc[:,:20] # 필요시 개수 제한
    weight = 1.5 #가중치 직접 설정가능 (오차 허용범위(높을 수록 둔감))
    min_value = 10000

    df_anomaly = Anomaly_Detect(df_,weight, min_value) #0/1 라벨링 필요해보임!!
    df_anomaly.to_csv('data/Anomaly_result.csv', encoding='cp949', index=False)
    df_anomaly_yes, df_anomaly_low = Extract_date(df_anomaly,df_)
    df_anomaly_key = key_keyword(df_anomaly_yes)
    df_anomaly_key.to_csv('data/anomaly_keyword.csv', encoding='cp949', index=False)
    df_anomaly_date = key_date(df_anomaly_yes)
    df_anomaly_date.to_csv('data/anomaly_date.csv', encoding='cp949', index=False)


    # 알림 기능(스케줄러 연결 필요)
    # 어제의 이상검색어가 있을 경우 카카오톡으로 알림(사용 안 할 경우 꺼놓기)---옵션으로 변경
    yesterday = str(datetime.now().date() - relativedelta(days=1))
    if df_anomaly_date['날짜'].iloc[-1] == yesterday:
        anomaly_yesterday = df_anomaly_date[df_anomaly_date['날짜'] == yesterday]['검색어'].values[0] #어제 이상치..
        message = f'{df_anomaly_date.날짜.iloc[-1]} 이상검색어 목록입니다. \n{anomaly_yesterday}'
        kakao_send_text(message)
    else:
        message = f'{df_anomaly_date.날짜.iloc[-1]} 이후 발견된 이상 검색어가 없습니다.'
        print(message)

if __name__ == "__main__":
    main()