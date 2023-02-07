import csv

from Relative_Value import *
from Absolute_Value import *
from config import *
_cfg = config


if __name__ == "__main__":
    
    # 검색어 목록 config에서 불러오기(데이터 비공개 목적으로 config파일에 포함했을 뿐, main파일에 리스트로 바로 작성해도 문제없습니다.)
    keyword_list = sum(_cfg['Keyword'].values(), [])
    #공백제거(한달치 검색량에 안 잡힘)
    keyword_list = [x.replace(' ','') for x in keyword_list]
    # 중복제거
    keyword_unique = []
    [keyword_unique.append(x) for x in keyword_list if x not in keyword_unique].clear() #None 반복 출력을 막기 위한 clear
    keyword_list = keyword_unique


    # 최대값을 갖는 검색어 찾기
    print('최대값을 갖는 검색어를 찾는 중입니다..')
    total_max_key, single_list, error_list = find_max_key(keyword_list)
    error_list = sum(error_list, [])
    total_max_key, single_list, final_error = find_error_list(error_list, total_max_key, single_list)
    keyword_list = [x for x in keyword_list if x not in final_error]
    print(f"최대값을 갖는 검색어: {total_max_key}")

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
    #검색량 상대값 산출
    print('검색어 상대값을 산출 중입니다..')
    df = search_amount(keyword_list,total_max_key,single_list)
    #검색량 상대값 저장
    date = str(datetime.now().date().strftime('%Y%m%d'))
    df.to_csv(f'data/result/search_result_relative{date}.csv', index=False)
    #df = pd.read_csv(f'data/result/search_result_relative{date}.csv')
    #df['날짜'] = df['날짜'].astype('datetime64[ns]')


    #상대값->절대값 변환
    print('상대값->절대값 변환 작업을 진행 중입니다..')
    final_df, error_per_average, MSE_average = real_amount(keyword_list,df,total_max_key,single_list)
    print(f"검색어 5개를 샘플링하여 계산한 오차율: {error_per_average}, MSE: {MSE_average}")
    #검색량 절대값 저장
    date = str(datetime.now().date().strftime('%Y%m%d'))
    final_df.to_csv(f'data/result/search_result_absolute{date}.csv', index=False)
    #df = pd.read_csv(f'data/result/search_result_absolute{date}.csv')
    #df['날짜'] = df['날짜'].astype('datetime64[ns]')
