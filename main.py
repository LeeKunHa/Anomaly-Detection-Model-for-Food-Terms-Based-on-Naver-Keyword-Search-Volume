import csv

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


    # 최대값을 갖는 검색어 찾기
    total_max_key, single_list, error_list = find_max_key(keyword_list)
    error_list = sum(error_list, [])
    total_max_key, single_list, final_error = find_error_list(error_list, total_max_key, single_list)
    keyword_list = [x for x in keyword_list if x not in final_error]
    
    
    # keyword_list 저장(final_error는 제외, single_list는 포함)
    with open('data/input_keyword/total_keyword.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(keyword_list)

    # 불러오기(# keyword_list를 바꾸지 않았으면 여기부터!!)
    keyword_list = []
    with open('data/input_keyword/total_keyword.csv','r',newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            keyword_list.append(row)
    keyword_list = sum(keyword_list, [])

    single_list = find_unmax_key(single_list)
    df = search_amount(keyword_list,total_max_key,single_list)
    #검색량 상대값 저장
    date = str(datetime.now().date().strftime('%Y%m%d'))
    df.to_csv(f'data/result/search_result{date}.csv', index=False)
    df = pd.read_csv(f'data/result/search_result{date}.csv')
    df['날짜'] = df['날짜'].astype('datetime64[ns]')

