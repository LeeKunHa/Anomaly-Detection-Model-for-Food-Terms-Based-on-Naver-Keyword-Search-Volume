#라이브러리
import pandas as pd
import urllib.request
import json
import random
from datetime import datetime
from dateutil.relativedelta import *

#자체 파일
from config import *
_cfg = config

#프로젝트용
#from Naver_Search_Amount.config import *
#_cfg = config

#경고제거
import warnings
warnings.filterwarnings(action='ignore')
#판다스 설정
pd.set_option('display.max_columns', 250)
pd.set_option('display.max_rows', 250)
pd.set_option('display.width', 100)
#소수점 아래 5자리까지 표시
pd.options.display.float_format = '{: .5f}'.format

class Parameter(): #수정시 다른 코드가 아닌 이 클래스만 수정하도록 분리
    def __init__(self):
        self.num = random.randrange(len(_cfg['NAVER_TREND'].items())/2) #생성한 api 수 만큼 설정
        self.client_id = _cfg['NAVER_TREND'][f'client_id{self.num}']
        self.client_secret = _cfg['NAVER_TREND'][f'client_secret{self.num}']
    # 요청 파라미터 설정
    """
    요청 결과 반환
    timeUnit - 'date', 'week', 'month'
    device - None, 'pc', 'mo'
    ages = [], ['1' ~ '11']
    gender = None, 'm', 'f'
    """
    startDate = str(datetime(2016, 1, 1).strftime('%Y-%m-%d')) #네이버API 최초 제공일자
    endDate = str(datetime.now().date().strftime('%Y-%m-%d')) #오늘
    timeUnit = 'date'
    device = ''
    ages = []
    gender = ''

class NaverDataLabOpenAPI():
    """
    네이버 데이터랩 오픈 API 컨트롤러 클래스
    """
    
    def __init__(self):
        """
        인증키 설정 및 검색어 그룹 초기화
        """
        parameter_ = Parameter() #randint 적용 시 id/secrect에 같은 숫자를 할당하기 위해(__init__을 한번실행하도록)
        self.client_id = parameter_.client_id
        self.client_secret = parameter_.client_secret
        self.keywordGroups = []
        self.url = "https://openapi.naver.com/v1/datalab/search"

    def add_keyword_groups(self, group_dict):
        """
        검색어 그룹 추가
        """
        keyword_gorup = {
            'groupName': group_dict['groupName'],
            'keywords': group_dict['keywords']
        }
        
        self.keywordGroups.append(keyword_gorup)
        #print(f">>> Num of keywordGroups: {len(self.keywordGroups)}")
        
    def get_data(self):
        # Request body
        body = json.dumps({
            "startDate": Parameter.startDate,
            "endDate": Parameter.endDate,
            "timeUnit": Parameter.timeUnit,
            "keywordGroups": self.keywordGroups,
            "device": Parameter.device,
            "ages": Parameter.ages,
            "gender": Parameter.gender
        }, ensure_ascii=False)
        
        # Results
        request = urllib.request.Request(self.url)
        request.add_header("X-Naver-Client-Id",self.client_id)
        request.add_header("X-Naver-Client-Secret",self.client_secret)
        request.add_header("Content-Type","application/json")
        response = urllib.request.urlopen(request, data=body.encode("utf-8"))
        rescode = response.getcode()
        if(rescode==200):
            # Json Result
            result = json.loads(response.read())
            
            df = pd.DataFrame(result['results'][0]['data'])[['period']]
            for i in range(len(self.keywordGroups)):
                tmp = pd.DataFrame(result['results'][i]['data'])
                tmp = tmp.rename(columns={'ratio': result['results'][i]['title']})
                df = pd.merge(df, tmp, how='left', on=['period'])
            self.df = df.rename(columns={'period': '날짜'})
            self.df['날짜'] = pd.to_datetime(self.df['날짜'])
            
        else:
            print("Error Code:" + rescode)
            
        return self.df

# 한번 실행
# 5개 이하 검색어만 허용
def one_search(keyword):
    if type(keyword) == str:
        naver = NaverDataLabOpenAPI()
        naver.add_keyword_groups({'groupName': keyword, 'keywords': [keyword]})
    elif type(keyword) == list: # 2개 이상 검색어 입력시 리스트로
        naver = NaverDataLabOpenAPI()
        for i in keyword: # 최대5개
            naver.add_keyword_groups({'groupName': i, 'keywords': [i]})
    df = naver.get_data()
    return df

# 최대값 찾기            
# 비율 값이 가장 큰(100) 검색어 찾기 
def max_key(data):
    data_ = data[data.values == 100]
    for i in data_.columns:
        try:
            if (data_[i].values == 100):
                return i
        except:
            if (data_[i].values[:1] == 100):
                return i

# 기준열인 100값 찾기 (오류가 발생한다면, 모든 값에 대해 검색값을 갖는 검색어가 없다는 의미)
def find_max_key(keyword_): #input 형태는 반드시 리스트
    keyword = keyword_.copy()
    #검색결과가 너무 적은 경우는 오류처리 하는 것으로 보임
    error_list = []
    #결측치가 있는 경우 다른 검색어에 대해서도 결측값이 생기는 점 확인. 이를 대비하기 위한 결측치 리스트 생성
    single_list = []
    
    #한번 미리 실행
    #처음 검색하는 단어가 검색결과가 없는 데이터면 결측값이 생기는 것을 방지
    while True:
        try:
            df = one_search(keyword[0])
            break
        except:
            error_list.append(keyword[0])
            keyword.remove(keyword[0])
            
    while len(df) != (datetime.now() - datetime(2016, 1, 1)).days: #첫 검색어는 모든 날짜에 값이 존재하는 검색어가 와야 함
        single_list.append(keyword[0])
        keyword.remove(keyword[0])
        while True:
            try:
                df = one_search(keyword[0])
                break
            except:
                error_list.append(keyword[0])
                keyword.remove(keyword[0])
        
    # 검색어 리스트가 4의 배수가 아니면 4의 배수로 만들기 (검색오류 대비)
    while (len(keyword)%4-1) != 0:
        keyword.append('임시')
        
    df_total = df.copy()

    # 검색어 리스트 값을 키워드로 지정
    for i in range(1, len(keyword)-3, 4):
        key1 = keyword[i]
        key2 = keyword[i+1]
        key3 = keyword[i+2]
        key4 = keyword[i+3]

        max_key_ = max_key(df) # 최대값 비교를 위한 복사
        
        # 데이터 프레임 정의 (one_search([max_key_,key1,key2,key3,key4]로 바꾸면 안 되나??)
        keyword_group_set = {
            'keyword_group_1': {'groupName': max_key_, 'keywords': [max_key_]},
            'keyword_group_2': {'groupName': key1, 'keywords': [key1]},
            'keyword_group_3': {'groupName': key2, 'keywords': [key2]},
            'keyword_group_4': {'groupName': key3, 'keywords': [key3]},
            'keyword_group_5': {'groupName': key4, 'keywords': [key4]}
        }
        
        naver = NaverDataLabOpenAPI()

        naver.add_keyword_groups(keyword_group_set['keyword_group_1'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_2'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_3'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_4'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_5'])
        
        try:
            df = naver.get_data()

            # 결측치 있는 최대값후보 single_list에 넣기
            while df[max_key(df)].isnull().any(): #결측값이 하나라도 있으면 max_key가 되면 안 된다.
                single_list.append(max_key(df))
                temp_list = [key1, key2, key3, key4]
                temp_list.remove(max_key(df))
                while (len(temp_list) != 3):
                    temp_list.append('임시')

                naver = NaverDataLabOpenAPI()
                naver.add_keyword_groups({'groupName': max_key_, 'keywords': [max_key_]})
                naver.add_keyword_groups({'groupName': temp_list[0], 'keywords': [temp_list[0]]})
                naver.add_keyword_groups({'groupName': temp_list[1], 'keywords': [temp_list[1]]})
                naver.add_keyword_groups({'groupName': temp_list[2], 'keywords': [temp_list[2]]})
                df = naver.get_data()

            #max_key가 바뀐 경우 기존 max_key의 100을 포함하는 값 지우고 병합
            if max_key_ == max_key(df):
                df_total = pd.merge(df_total,df, how='left', on=["날짜",max_key(df)])
            if max_key_ != max_key(df):
                df_total = df_total.drop([max_key_],axis=1)
                df_total = pd.merge(df_total,df, how='left', on="날짜")
                
        except:
            error_list.append([key1,key2,key3,key4])
    
    if len(single_list) > 0 : #single_list에 total_max_key를 추가하는 이유는, total_max_key와 비교하기 위함
        single_list.insert(0, max_key(df_total))
    return max_key(df_total), single_list, error_list #single_list는 결측값이 있는 검색어 중 최대값일 가능성이 있는 단어(여기서는 최종단계가 아닌 진행 단계에서의 최대값 중 결측값을 갖는 단어)

### error_list 찾기
def find_error_list(error_list, total_max_key, single_list):
    final_error = []
    for i in error_list:
        try:
            df = one_search([total_max_key, i])
            # 결측치 있는 최대값후보 single_list에 넣기
            if total_max_key != max_key(df):
                if df[max_key(df)].isnull().any(): #결측값이 하나라도 있으면 max_key가 되면 안 된다.
                    single_list.append(max_key(df))
                else:
                    total_max_key = max_key(df)
        except:
            final_error.append(i)
    return total_max_key, single_list, final_error


### single_list 중 total_max_key보다 작을 수도 있는 값 추가
#결측치 있던 max_key()후보와 total_max_key를 다시 비교해서 최종 total_max_key보다 작은 값은 포함
def find_unmax_key(keyword):
    if len(keyword) == 0:
        #print("모든 검색어가 이미 포함되었습니다.")
        return []
    
    elif len(keyword) > 0:
        single_list = []

        # 검색어 리스트가 4의 배수가 아니면 4의 배수로 만들기 (검색오류 대비)
        while (len(keyword)%4-1) != 0:
            keyword.append('임시')

        #한번 미리 실행
        df = one_search(keyword[0])
        df_total = df.copy()

        # 검색어 리스트 값을 키워드로 지정
        for i in range(1, len(keyword)-3, 4):
            key1 = keyword[i]
            key2 = keyword[i+1]
            key3 = keyword[i+2]
            key4 = keyword[i+3]

            # 데이터 프레임 정의
            keyword_group_set = {
                'keyword_group_1': {'groupName': keyword[0], 'keywords': [keyword[0]]},
                'keyword_group_2': {'groupName': key1, 'keywords': [key1]},
                'keyword_group_3': {'groupName': key2, 'keywords': [key2]},
                'keyword_group_4': {'groupName': key3, 'keywords': [key3]},
                'keyword_group_5': {'groupName': key4, 'keywords': [key4]}
            }

            naver = NaverDataLabOpenAPI()

            naver.add_keyword_groups(keyword_group_set['keyword_group_1'])
            naver.add_keyword_groups(keyword_group_set['keyword_group_2'])
            naver.add_keyword_groups(keyword_group_set['keyword_group_3'])
            naver.add_keyword_groups(keyword_group_set['keyword_group_4'])
            naver.add_keyword_groups(keyword_group_set['keyword_group_5'])
            df = naver.get_data()

            if keyword[0] != max_key(df):
                for i in [key1,key2,key3,key4]:
                    df_ = df.iloc[:,1:]
                    if df_[keyword[0]].max() < df_[i].max():
                           single_list.append(i)
        #print('정상적으로 처리되었습니다.')                  
        return single_list #single_list는 결측값이 있는 검색어 중 total_max_key(결측값이 없는 검색어 중 최대값을 갖는 검색어) 최대값일 가능성이 있는 단어


#total_max_key를 기준(100)으로 전체 검색어에 대한 상대적 검색량 값 최종 산출
def search_amount(keyword,total_max_key,single_list):
    keyword = [x for x in keyword if x not in single_list] #single_list 검색어는 제외. 추후 실제값으로 합칠 예정
    # 리스트 원래 순서 저장
    keyword_raw = keyword.copy()

    # find_max_key를 맨 앞으로 (나중에 완성되면 total_max_key를 max_key(keyword) 로)
    keyword.remove(total_max_key)
    keyword.insert(0,total_max_key)

    # 검색어 리스트가 4의 배수가 아니면 4의 배수로 만들기 (검색오류 대비)
    while (len(keyword)%4-1) != 0:
        keyword.append('임시')

    #한번 미리 실행
    naver = NaverDataLabOpenAPI()
    naver.add_keyword_groups({'groupName': keyword[0], 'keywords': [keyword[0]]})
    df = naver.get_data()
    df_total = df.copy()


    # 검색어 리스트 값을 키워드로 지정
    for i in range(1, len(keyword)-3, 4):
        key1 = keyword[i]
        key2 = keyword[i+1]
        key3 = keyword[i+2]
        key4 = keyword[i+3]

        # 데이터 프레임 정의
        keyword_group_set = {
            'keyword_group_1': {'groupName': keyword[0], 'keywords': [keyword[0]]},
            'keyword_group_2': {'groupName': key1, 'keywords': [key1]},
            'keyword_group_3': {'groupName': key2, 'keywords': [key2]},
            'keyword_group_4': {'groupName': key3, 'keywords': [key3]},
            'keyword_group_5': {'groupName': key4, 'keywords': [key4]}
        }


        naver = NaverDataLabOpenAPI()

        naver.add_keyword_groups(keyword_group_set['keyword_group_1'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_2'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_3'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_4'])
        naver.add_keyword_groups(keyword_group_set['keyword_group_5'])
        df = naver.get_data()
        
        df_total = pd.merge(df_total,df, how='left', on=["날짜",keyword[0]])

    #중복값/4의 배수를 만들기 위해 생성한 값 삭제
    if keyword[-1] == '임시':
        #df_total = df_total.T.drop_duplicates().T
        df_total = df_total[df_total.columns.drop(list(df_total.filter(regex='임시')))]
        #df.drop(df[df.columns[pd.Series(df.columns).str.startswith('임시')]], axis=1)
    
    #원래 리스트 순서대로 정렬
    keyword_raw.insert(0, '날짜')
    df = df_total[keyword_raw]
    return df