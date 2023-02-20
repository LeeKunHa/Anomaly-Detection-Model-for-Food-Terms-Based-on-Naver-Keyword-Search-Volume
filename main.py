# 라이브러리
import pandas as pd
import os
# 자체 파일
from Naver_Search_Amount import main as nsa
from Anomaly_Detection_prophet import main as adp
from News_Crawler import main as nc
from Text_Analyze import main as ta

def main():
    df_date = pd.read_csv('Anomaly_Detection_prophet/data/result_for_crawler.csv', encoding='cp949')
    for i in range(len(df_date)):
        for j in range(len(df_date['시작일자'][i].strip('[]').split())):
            search_=df_date['검색어'][i]
            start_date=str(df_date['시작일자'][i].strip('[]').split()[j])[:8]
            end_date=str(df_date['종료일자'][i].strip('[]').split()[j])[:8]
            print(search_,start_date,end_date)
            all_news_df, naver_news_df = nc.main(search_, start_date, end_date,'No')

if __name__ == "__main__":
    main()
