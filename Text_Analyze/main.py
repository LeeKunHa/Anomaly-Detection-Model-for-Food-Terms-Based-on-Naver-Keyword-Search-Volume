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

def main(recent_file):        
    # 파일 읽어오기
    df = pd.read_csv(recent_file)
    
    if len(df) == 0: return 'pass' # 뉴스가 하나도 없는 경우 통과

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
    tfidf(df, file_name_)
    
    # 완료한 결과 resume_list에 추가
    resume_list = open("resume_list.txt", 'a', encoding='cp949')
    resume_list.write(recent_file[27:-4]+'\n')
    resume_list.close()

if __name__ == "__main__":
    #df, key_keyword, recent_file = main()
    
    # 폴더 내 모든 파일 읽기
    file_path = ('../News_Crawler/data/')
    files = glob.glob(f'{file_path}title_*.csv')
    files = natsorted(files)
    
    # 이미 저장된 파일 읽어오기(이어하기 옵션)
    resume_ = []
    with open("resume_list.txt", "r", encoding='cp949') as resume_list:
        for i in resume_list.readlines():
            resume_.append(i[:-1])
    files = [x for x in files if x[27:-4] not in resume_]

    for recent_file in files:
        main(recent_file)