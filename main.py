#크롤링시 필요한 라이브러리 불러오기
import datetime
import sys
import pandas as pd

#자체 파일
from News_Crawler import *

def main(search_, start_date, end_date, recursive='No'): #재귀로 사용되는 경우라면 저장안 하도록 recursive 기본값 설정
    #####뉴스크롤링 시작#####
    #검색어 입력
    #search_ = input("검색할 키워드를 입력해주세요:")
    search = '"'+search_+'"' #정확하게 뉴스에 포함되는 경우만 가져오도록 "" 로 감싸기
    #검색 시작할 날짜 입력
    #start_date = input("시작날짜: ")
    S_Y = int(start_date[:4])
    S_M = int(start_date[4:6])
    S_D = int(start_date[6:])
    s1 = datetime.date(S_Y,S_M,S_D).strftime("%Y.%m.%d")
    s2 = datetime.date(S_Y,S_M,S_D).strftime("%Y%m%d")
    #검색 종료할 날짜 입력
    #end_date = input("종료날짜: ")
    E_Y = int(end_date[:4])
    E_M = int(end_date[4:6])
    E_D = int(end_date[6:])
    e1 = datetime.date(E_Y,E_M,E_D).strftime("%Y.%m.%d")
    e2 = datetime.date(E_Y,E_M,E_D).strftime("%Y%m%d")
    if s1 > e1: #input 일때만 남기기
        print("시작날짜가 종료날보다 빠릅니다.")
        sys.exit()

    # 크롤링한 데이터 축적을 위한 기본값 생성
    page = 1
    #global naver_news_df
    naver_news_df = pd.DataFrame(columns=['date','title','link','content', 'press']) #내용을 가져올 수 있는 '네이버뉴스'
    all_news_df = pd.DataFrame(columns=['date','title','link', 'press']) #내용을 가져오지 않고 제목만(모든 언론사)
    time_step = datetime.date(S_Y,S_M,S_D).strftime("%Y-%m-%d") #날짜 저장용
    every_date = []
    #every_url = []
    not_naver_urls = [] #본문내용을 추가로 가져올 크롤러 작성 용이함을 위해
    
    # url 생성
    while True:
        url_ = f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&sort=2&ds={s1}&de={e1}&nso=so:dd,p:from{s2}to{e2}&start={page}"

        news_url = []
        url = articles_crawler(url_)
        news_url.append(url)
        
        #종료조건1
        if len(url) == 0: #stop(all_news_df, naver_news_df, search_, start_date, end_date)
            #중복 행 지우기
            all_news_df = all_news_df.drop_duplicates(keep='first',ignore_index=True)
            naver_news_df = naver_news_df.drop_duplicates(keep='first',ignore_index=True)
            #데이터 프레임 저장
            now = datetime.datetime.now()
            if recursive == 'No': #재귀함수로 다시 들어온 경우가 아니라면 저장실행
                all_news_df.to_csv(f'./data/news_raw/title_{search_}_{start_date}_{end_date}.csv', encoding='utf-8-sig',index=False)
                naver_news_df.to_csv(f'./data/news_raw/naver_{search_}_{start_date}_{end_date}.csv', encoding='utf-8-sig',index=False)
            return all_news_df, naver_news_df
        
        #모든 뉴스 크롤러 실행(모든 뉴스의 제목)
        raw_df_all = all_news_crawler(url_)
        all_news_df = pd.concat([all_news_df, raw_df_all])
        
        #제목, 링크, 내용 담을 리스트 생성
        news_url_1 = []

        #1차원 리스트로 만들기(내용 제외)
        makeList(news_url_1,news_url)
        
        #NAVER 뉴스만 남기기(내용을 가져올 수 있는 네이버 뉴스)
        naver_urls = []
        for i in range(len(news_url_1)):
            if "news.naver.com" in news_url_1[i]:
                not_naver_urls.append(news_url_1[i])
                naver_urls.append(news_url_1[i])
            elif not "news.naver.com" in news_url_1[i]:
                not_naver_urls.append(news_url_1[i])

        raw_df_naver = naver_news_crawler(naver_urls)
        naver_news_df = pd.concat([naver_news_df, raw_df_naver])
        
        # 진행날짜 표시
        if all_news_df['date'].values[-1] != time_step:
                print(all_news_df['date'].values[-1])
        time_step = all_news_df['date'].values[-1]        
        
        page = page+10

        #종료조건2
        if page == 4001:
            print('400페이지를 초과해 추가 크롤링을 진행합니다.')
            #400페이지 넘으면 재귀함수를 통해 합치기
            all_news_df2, naver_news_df2 = main(search_, time_step.replace('-', ''), end_date, 'Yes')
            all_news_df = pd.concat([all_news_df, all_news_df2])
            naver_news_df = pd.concat([naver_news_df, naver_news_df2])
            #stop(all_news_df, naver_news_df, search_, start_date, end_date)
            #중복 행 지우기
            all_news_df = all_news_df.drop_duplicates(keep='first',ignore_index=True)
            naver_news_df = naver_news_df.drop_duplicates(keep='first',ignore_index=True)
            #데이터 프레임 저장
            now = datetime.datetime.now()
            all_news_df.to_csv(f'./data/news_raw/title_{search_}_{start_date}_{end_date}.csv', encoding='utf-8-sig',index=False)
            naver_news_df.to_csv(f'./data/news_raw/naver_{search_}_{start_date}_{end_date}.csv', encoding='utf-8-sig',index=False)
            return all_news_df, naver_news_df


# main 안에 인자는 '검색어', '시작일', '종료일'
if __name__ == "__main__":
    search_keyword = input(f'검색어를 입력하세요: ')
    start_date = input(f'시작일자를 입력하세요(YYMMDD): ')
    end_date = input(f'종료일자를 입력하세요(YYMMDD): ')
    all_news_df, naver_news_df = main(search_keyword, start_date, end_date)
