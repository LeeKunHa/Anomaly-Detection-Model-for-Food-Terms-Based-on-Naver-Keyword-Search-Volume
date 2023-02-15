# 라이브러리
import pandas as pd
import os
import re
import glob
from natsort import natsorted


# 자체 파일
from keyword_extraction import *
from config import *
_cfg = config

# 파일 읽어오기
files = glob.glob('../News_Crawler/data/news_raw/title_*.csv') #최신파일 읽어오기(폴더 경로 입력으로 바꾸기)
recent_file = natsorted(seq=files, reverse=True)[0]
df = pd.read_csv(recent_file)
# 텍스트 전처리
df['title_c'] = df.apply(clean_text, axis=1)
# 형태소 분석기 가동
df = morphological_analyzer(df)
# 불용어 적용
stopword = _cfg['STOP_WORD'] #stopword = [] #(직접 입력도 가능)
df = apply_stopword(df,stopword)
# 동의어/유의어 사전
synonym_dict = _cfg['SYNONYM_DICT']
df = apply_synonym_dict(df,synonym_dict) #synonym_dict = [] #(직접 입력도 가능)
df.to_csv('data/result/news_noun.csv', encoding='utf-8-sig', index=False)
