# 라이브러리
import pandas as pd
import glob
from natsort import natsorted

# 자체 파일
from keyword_extraction import *
from text_analyze import *
from config import *
_cfg = config

#프로젝트용
#from Text_Analyze.keyword_extraction import *
#from Text_Analyze.text_analyze import *
#from Text_Analyze.config import *
#_cfg = config

def main():
    # 최신파일 읽기
    #files = glob.glob('../News_Crawler/data/title_*.csv') #최신파일 읽어오기(폴더 경로 입력으로 바꾸기)--생성 날짜기준으로 변경
    #recent_file = natsorted(seq=files, reverse=True)[0]

    # 폴더 내 모든 파일 읽기
    file_path = ('../News_Crawler/data/')
    files = glob.glob(f'{file_path}title_*.csv')
    files = natsorted(files)
    for recent_file in files:
    
        # 파일 읽어오기
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
        file_name_ = f'{recent_file[27:-19]}{recent_file[-19:-12]}{recent_file[-12:-4]}'

        #워드클라우드
        word_counter_ = make_corpus(df)
        draw_word_cloud(word_counter_, file_name_)

        #SNA
        edges = make_edge_list(df)
        draw_SNA(df, edges, file_name_)
        #plt.show() # 시각화 결과 창 실행

        #Tf-idf
        key_keyword = tfidf(df)
        return df, key_keyword, recent_file


if __name__ == "__main__":
    df, key_keyword, recent_file = main()
    print(recent_file)
    print(key_keyword)
