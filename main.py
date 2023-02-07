from config import *
_cfg = config

if __name__ == "__main__":
    # 검색어 선택
    # 자체 검색어
    keyword_list = _cfg['Keyword']['User_list']
    # 식신 카테고리
    keyword_list = _cfg['Keyword']['Siksin']
    # 식품첨가물용어집(식품안전나라 용어사전)
    keyword_list = _cfg['Keyword']['Food_Safety_Dict']
    # 네이버 식품 카테고리 인기검색어 top500
    keyword_list = _cfg['Keyword']['Naver_Food_Rank']
    # 요식업 브랜드명
    keyword_list = _cfg['Keyword']['Food_Brand']
    # 식품안전정보 검색어(식품안전정보원 글로벌 정보부)
    keyword_list = _cfg['Keyword']['Food_Safety_Issue']
    # 식품안전나라 검색어 기록(22/09/13 기준)
    keyword_list = _cfg['Keyword']['Food_Safety_Search']

    # 검색어 통합
    keyword_list = sum(_cfg['Keyword'].values(), [])
    # 중복제거
    keyword_unique = []
    [keyword_unique.append(x) for x in keyword_list if x not in keyword_unique].clear() #None 반복 출력을 막기 위한 clear
    keyword_list = [x.replace(' ','') for x in keyword_list] #공백제거(한달치 검색량에 안 잡힘)