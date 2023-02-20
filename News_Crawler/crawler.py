#크롤링시 필요한 라이브러리 불러오기
from bs4 import BeautifulSoup
import requests
import re
import datetime
import pandas as pd

# html에서 원하는 속성 추출하는 함수 만들기 (기사, 추출하려는 속성값)
def news_attrs_crawler(articles,attrs):
    attrs_content=[]
    for i in articles:
        attrs_content.append(i.attrs[attrs])
    return attrs_content

#html생성해서 기사크롤링하는 함수 만들기(url): 링크를 반환
def articles_crawler(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    #html 불러오기
    original_html = requests.get(url,headers=headers)
    html = BeautifulSoup(original_html.text, "html.parser")
    url_naver = html.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
    url = news_attrs_crawler(url_naver,'href')
    return url
    
#제목, 링크, 내용 1차원 리스트로 꺼내는 함수 생성
def makeList(newlist, content):
    for i in content:
        for j in i:
            newlist.append(j)
    return newlist


# 모든 언론사의 '제목' 포함 크롤링
def all_news_crawler(url_):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    original_html = requests.get(url_,headers=headers)
    html = BeautifulSoup(original_html.text, "html.parser")
        
    # 뉴스 제목 가져오기
    url_news = html.select("a.news_tit")
    news_titles = news_attrs_crawler(url_news,'title')

    # 언론사명 가져오기(텍스트->언론사명만)
    url_news = html.select("div.info_group > a")
    news_press = list(map(lambda x: x.get_text(), url_news))
    news_press_ = list(map(lambda x: x.string, url_news))
    news_press = [x for x in news_press if x not in news_press_]
    
    # link 가져오기
    url_news = html.select("a.news_tit")
    news_urls = news_attrs_crawler(url_news,'href')
    
    # 날짜 가져오기(텍스트->날짜만)
    url_news = html.select("div.info_group > span")
    news_dates = list(map(lambda x: x.string, url_news))
    news_dates_ = list(map(lambda x: x.get_text(), url_news))
    news_dates = [x for x in news_dates if x in news_dates_]
    
    #00시간전/00일전 으로 뜨는 문제
    #현재시간-'00시간 전'이 양수면 오늘날짜로
    news_dates = list(map(lambda x: datetime.datetime.now().strftime("%Y.%m.%d") if ('시간 전' in x) and (datetime.datetime.now().hour >= int(x.split('시간')[0])) else x, news_dates))
    #현재시간-'00시간 전'이 음수면 어제날짜로.
    news_dates = list(map(lambda x: (datetime.datetime.now() - datetime.timedelta(hours=int(x.split('시간')[0]))).strftime("%Y.%m.%d") if ('시간 전' in x) and (datetime.datetime.now().hour <= int(x.split('시간')[0])) else x, news_dates))
    #'00일 전'이면 오늘날짜-00일만큼
    news_dates = list(map(lambda x: (datetime.datetime.now() - datetime.timedelta(days=int(x.split('일')[0]))).strftime("%Y.%m.%d") if '일 전' in x else x, news_dates))
    # 날짜 전처리       
    pattern = '([0-9]+)'
    news_dates = list(map(lambda x: re.findall(pattern=pattern, string=x), news_dates))
    news_dates = list(map(lambda x: '-'.join(x), news_dates))
        
    #데이터 프레임 만들기
    raw_df_all = pd.DataFrame({'date':news_dates,'title':news_titles,'link':news_urls,'press':news_press})
        
    return raw_df_all

# 네이버 뉴스의 '내용'포함 크롤링
def naver_news_crawler(naver_urls):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
    naver_dates = []
    naver_titles = []
    naver_contents = []
    naver_press = []
    # 뉴스 본문내용 크롤링
    for i in naver_urls:
        #각 기사 html get하기
        news = requests.get(i,headers=headers)
        news_html = BeautifulSoup(news.text,"html.parser")

        # 뉴스 제목 가져오기
        title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
        if title == None:
            title = news_html.select_one("#content > div.end_ct > div > h2")

        # 뉴스 본문 가져오기
        content = news_html.select("div#dic_area")
        if content == []:
            content = news_html.select("#articeBody")

        # 기사 텍스트만 가져오기
        # list합치기
        content = ''.join(str(content))

        # 언론사명 가져오기
        try:
            press = news_html.select("#ct > div.media_end_head.go_trans > div.media_end_head_top > a > img.media_end_head_top_logo_img.light_type")[0]["title"]
        except:
            try:
                press = news_html.select("#content > div.end_ct > div > div.press_logo > a > img")[0]["alt"] #연합뉴스
            except:
                try:
                    press = news_html.select("#pressLogo > a > img")[0]['alt'] #스포츠서울
                except:
                    press = ''

        # html태그제거 및 텍스트 다듬기
        pattern1 = '<[^>]*>'
        title = re.sub(pattern=pattern1, repl='', string=str(title))
        content = re.sub(pattern=pattern1, repl='', string=content)
        pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
        content = content.replace(pattern2, '')
        naver_titles.append(title)
        naver_contents.append(content)
        naver_press.append(press)
        
        # 뉴스 날짜 가져오기
        try:
            html_date = news_html.select_one("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
            news_date = html_date.attrs['data-date-time']
        except AttributeError:
            news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
            news_date = re.sub(pattern=pattern1,repl='',string=str(news_date))
        
        
        # 날짜 전처리    
        pattern = '([0-9]+)'
        news_date = re.findall(pattern=pattern, string=news_date)
        news_date = '-'.join(news_date)

        #시간분초 삭제
        news_date = news_date[:10]
        #list(map(lambda x: str(x)[:10], news_date))
        
        # 날짜 가져오기
        naver_dates.append(news_date)
        
    #데이터 프레임 만들기
    raw_df_naver = pd.DataFrame({'date':naver_dates,'title':naver_titles,'link':naver_urls,'content':naver_contents,'press':naver_press})
    return raw_df_naver