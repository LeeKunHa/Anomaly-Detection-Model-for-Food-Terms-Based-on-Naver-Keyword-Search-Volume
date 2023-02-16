# 라이브러리
import pandas as pd
import re
from konlpy.tag import Mecab
mecab = Mecab(dicpath=r"C:/mecab/mecab-ko-dic")

# 자체 파일
from config import *
_cfg = config

#프로젝트용
#from Text_Analyze.config import *
#_cfg = config

""" 필요 없는 문자 제거 """
def clean_text(row):
    text = row['title']
    pattern = r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("E-mail제거 : " , text , "\n")
    pattern = r'(http|ftp|https)://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("URL 제거 : ", text , "\n")
    pattern = '([ㄱ-ㅎㅏ-ㅣ]+)'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("한글 자음 모음 제거 : ", text , "\n")
    pattern = '<[^>]*>'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("태그 제거 : " , text , "\n")
    pattern = r'\([^)]*\)'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("괄호 및 괄호안 글자 제거 :  " , text , "\n")
    pattern = r'[^\w\s]'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("특수기호 제거 : ", text , "\n" )
    pattern = r'[^\w\s]'
    text = re.sub(pattern=pattern, repl='', string=text)
    # print("필요없는 정보 제거 : ", text , "\n" )
    text = text.strip()
    # print("양 끝 공백 제거 : ", text , "\n" )
    text = " ".join(text.split())
    # print("중간에 공백은 1개만 : ", text )
    return text

# 형태소 분석기 실행
def morphological_analyzer(df_):
    df = df_.copy()
    df['keyword_mecab'] = ''
    for idx_line in range(len(df)):
        nouns_list_mecab = mecab.nouns(df['title_c'].loc[idx_line])
        nouns_list_mecab_c = [nouns for nouns in nouns_list_mecab if len(nouns) > 1]    # 한글자는 이상한게 많아서 2글자 이상
        df.loc[idx_line]['keyword_mecab'] = nouns_list_mecab_c #자체수정
    return df

# 불용어 지정
def apply_stopword(df_,stopword):
    df = df_.copy()
    for i in range(len(df['keyword_mecab'])):
        df['keyword_mecab'][i] = [x for x in df['keyword_mecab'][i] if x not in stopword]
    return df

# 동의어/유의어 사전 지정
def apply_synonym_dict(df_, synonym_dict):
    df = df_.copy()
    apply_mapping = {word : k for k, v in synonym_dict.items() for word in v}
    for i in range(len(df['keyword_mecab'])):
        df['keyword_mecab'][i] = sum(pd.DataFrame([x for x in df['keyword_mecab'][i]]).replace(apply_mapping, regex=True).values.T.tolist(), [])
    df['keyword_mecab']
    return df
