# 카카오 API
# -https://developers.kakao.com/tool/rest-api/open/post/v2-api-talk-memo-default-send
import json
import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta

# 자체 파일
from config import *
_cfg = config
def kakao_send_text(message):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    # 사용자 토큰
    headers = {
        "Authorization": "Bearer " + _cfg['Kakao_Authorization']
    }
    data = {
        "template_object" : json.dumps({ "object_type" : "text",
                                        "text" : message,
                                        "link" : {
                                                    "web_url" : "www.naver.com",
                                                    "mobile_web_url": "https://developers.kakao.com"
                                                }
        })
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    if response.json().get('result_code') == 0:
        print('메시지를 성공적으로 보냈습니다.')
    else:
        print('메시지를 성공적으로 보내지 못했습니다. 오류메시지 : ' + str(response.json()))
        # 이미지 보내는 방법 추가 필요