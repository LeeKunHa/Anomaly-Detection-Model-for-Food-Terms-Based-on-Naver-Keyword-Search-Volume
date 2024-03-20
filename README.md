## 네이버 검색량 기반 식품 검색어 이상탐지모델 구축 (Anomaly Detection Model for Food Terms Based on Naver Keyword Search Volume)
[주요 과정은 PDF 파일을 참고해주세요](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/blob/main/%EB%84%A4%EC%9D%B4%EB%B2%84%20%EA%B2%80%EC%83%89%EB%9F%89%20%EB%8D%B0%EC%9D%B4%ED%84%B0%20%EA%B8%B0%EB%B0%98%20%EC%8B%9D%ED%92%88%20%EA%B2%80%EC%83%89%EC%96%B4%20.pdf)


### **① 네이버 데이터랩 ‘통합검색어 트렌드 API’를 이용한 ‘상대적 검색량’ 추출**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/e311a776-90ae-4014-876a-653ffebf52d7)

### **② ‘NAVER Search Ad API(네이버광고API)’를 이용한 검색량 상대값→절대값 변환**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/edf8ccb8-2f2b-4e67-a7cd-2a56b9025e09)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/8dad8796-26d4-4b54-b140-797846307530)

### **③ 시계열 예측 모델(prophet)을 이용한 검색어의 ‘일반적인 검색량’ 예측**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/47e0ede8-8705-4946-92b7-8bd7e8deb6b8)

### **④ 일반적인 검색량 대비 실제 검색량이 높은 이상 항목 탐지(Anomaly Detection)**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/c582f73e-3d42-4ab5-aefd-3c82d56c6c82)

### **⑤ 이상 검출 항목 라벨링 및 전처리(‘[검색어, 시작일자, 종료일자]’ 형태로 변환)**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/84122fa1-6441-4011-bf30-ac3d2fd55f1f)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/c222e191-b19d-44eb-be18-734e53befaf8)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/cb364d4a-da25-4672-ae2d-4a2272e57bc9)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/fc07a1bc-8d1f-4009-9587-b41e7240239c)

### **⑥ 검출된 검색어와 기간에 해당하는 뉴스 크롤링**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/0eae3b88-0b29-4189-a569-053336739ea5)

### **⑦ 자연어처리를 위한 사전 구축 및 텍스트 전처리**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/329c83af-4d0f-4d3d-852f-c93e485b01da)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/8ffe88ce-ef3c-4d82-b4c3-f8bafe90931f)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/25717408-ddb4-4bbe-a938-d0e9abb900ea)

### **⑧ 형태소 분석기를 이용한 뉴스 제목 내 명사 추출**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/49693482-8975-45e5-8241-63a7ad9abdd1)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/46a08c62-d458-4459-b951-5268906dc8fe)

### **⑨ 검출된 검색어와 기간에 대한 뉴스 내 주요 키워드 분석 (SNA,워드클라우드,TF-IDF)**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/5e129583-561b-470e-b7dd-8af2c218d788)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/099f60b4-0278-4d95-a219-cc7380849196)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/ae8181bf-1b89-4ccc-81dd-5bd49e3604d3)

### **⑩ 스케줄러를 이용한 이상검색량 자동점검 및 업데이트(어제 이상검색량이 발생할 경우 카카오톡 나에게 보내기를 통해 알림 제공)**
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/68804f1e-7502-41bd-a1db-7340b42fe2df)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/7f4cacc3-2233-493d-bffe-aeb0b6a7597b)
![image](https://github.com/LeeKunHa/Anomaly-Detection-Model-for-Food-Terms-Based-on-Naver-Keyword-Search-Volume/assets/88371786/9246ef5f-d4ea-4b6f-b527-bd9f27d9afa5)
