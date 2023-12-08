from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import json
import requests

with open('secrets.json') as f:
    secrets = json.loads(f.read())

# FRONTEND_URL = secrets['frontend_url']
# BUCKET_NAME = secrets['aws_s3_bucket']
# ACCESS_KEY = secrets['aws_access_key']
# SECRET_KEY = secrets['aws_secret_key']
# LOCATION = secrets['aws_s3_location']
# S3_URL = f'https://{BUCKET_NAME}.s3.{LOCATION}.amazonaws.com'
CLOVA_HOST = secrets['clova_host']
CLOVA_API_KEY = secrets['clova_api_key']
CLOVA_API_KEY_PRIMARY_VAL = secrets['clova_api_key_primary_val']
CLOVA_REQUEST_ID = secrets['clova_request_id']

app = FastAPI()

class Diary(BaseModel):
    name: str = "토리"
    title: Optional[str] = ""
    contents: Optional[str] = "오늘 밤에 자전거를 탔다. 자전거는 처음 탈 때는 좀 중심잡기가 힘들었다. 그러나 재미있었다. 자전거를 잘 타서 엄마, 아빠 산책 갈 때 나도 가야겠다."
    keyword: Optional[str] = "마법"

class StoryTitleText(BaseModel):
    title: str = ""
    texts: List[str] = []
    
class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }
        try: 
            with requests.post(self._host + '/testapp/v1/chat-completions/HCX-002',
                            headers=headers, json=completion_request, stream=True) as r:

                results = r.text
                result = results.split("\n\n")[-3]
                
                data = result.split("\n")[-1][5:]
                data = json.loads(data)
                content = data['message']['content']
                # print(content)
                return content
        except:
            return None

completion_executor = CompletionExecutor(
    host=CLOVA_HOST,
    api_key=CLOVA_API_KEY,
    api_key_primary_val=CLOVA_API_KEY_PRIMARY_VAL,
    request_id=CLOVA_REQUEST_ID
)

def create_title(story: str):
    preset_text = [{"role":"system",
                    "content":"- 여섯 개 이하의 단어로 구성된 짧은 길이의 동화 제목을 만드는 작가입니다.\
                        \n- 아이들이 재미있도록 창의적인 단어를 사용합니다."},
                    {"role":"user","content":f"동화 이야기: {story} \n제목:"}]

    request_data = {
        'messages': preset_text,
        'maxTokens': 3573,
        'temperature': 1.0,
        'topK': 0,
        'topP': 0.8,
        'repeatPenalty': 8.0,
        'stopBefore': [],
        'includeAiFilters': True
    }
    return completion_executor.execute(request_data).strip("\"")

def create_story(diary: Diary):
    preset_text = [{"role":"system",
                    "content":"- 초등학교 저학년 어린이가 입력한 일기를 주어진 키워드의 의미가 반영된 동화로 바꾸어 들려주는 선생님입니다.\
                        \n- 답변을 150글자 이하의 약 5개의 문단으로 구성합니다.\
                        \n- 폭력적이거나 선정적인 내용이 있는 경우 \"다시 작성해주세요.\"라고 답변합니다.\
                        \n- 주인공은 성별이 없습니다.\
                        \n- \"해요체\"를 사용해주세요.\n"},
                    {"role":"user",
                     "content":"일기:  가장 기억에 남는 꿈은 세상 사람들의 색깔이 점점 없어져서 흑백 세상이 되는 꿈이다. 색깔이 완전히 없어진 사람은 그 세상에서 사라져버리는 무서운 꿈이었다!\
                        \n이야기 내용에 반영할 키워드: 우주\
                        \n주인공 이름:  고양이\
                        \n동화:"},
                    {"role":"assistant",
                    "content":"고양이는 한 번 꾸었던 꿈을 잊을 수 없었어요. 그 꿈은 세상의 색깔이 점점 사라져서 흑백 세상이 되는 꿈이었어요. 고양이는 그 꿈에서 색깔이 완전히 없어진 사람들이 사라지는 것을 보며 무서워했어요.\
                        \n\n그 꿈을 꿀 때마다 고양이는 더 이상 그런 세상이 되지 않기를 바랐어요. 그래서 어느 날, 고양이는 우주선을 타고 다른 행성을 찾아가기로 했어요. 그곳에서 색깔이 풍부한 생물들과 만나고, 아름다운 풍경을 볼 수 있을 것이라고 생각했어요.\
                        \n\n우주선을 타고 여러 행성을 탐험하던 도중, 고양이는 한 행성에서 특별한 것을 발견했어요. 그 행성에 사는 생물들은 빛나는 색깔을 지니고 있었어요. 그들은 다양한 색으로 빛나면서, 환상적인 미소로 인사했어요.\
                        \n\n고양이는 이 행성의 생물들과 함께 지내면서, 색깔이 사라지는 꿈을 이야기했어요. 그들은 꿈에 대해 생각하고 논의하며, 함께 색깔의 중요성을 이해하고자 했어요.\
                        \n\n그리고 어느 날, 그 행성에서 특별한 약초를 발견했어요. 그 약초를 먹으면 꿈 속에서 색깔이 사라지는 일은 더 이상 일어나지 않을 것이라고 말했어요. 고양이는 그 약초를 가져와서 다른 행성의 사람들과 나누었어요.\
                        \n\n그리고 이야기는 퍼져나갔어요. 모든 행성의 사람들이 그 약초를 먹고 꿈을 꾸면, 색깔은 사라지지 않을 것이라는 희망이 생겼어요. 이후로, 모든 사람들은 색깔을 소중히 여기고, 함께 아름다운 세상을 만들기 위해 노력했어요.\
                        \n\n고양이는 그 꿈이 무서웠지만, 그 꿈을 통해 사람들이 색깔의 중요성을 깨달았고, 변화를 이룰 수 있었어요. 그리고 이제 고양이는 더 이상 그런 꿈을 꾸지 않아도 되었어요. 색깔이 있는 아름다운 세상에서 모험을 즐깁니다."},
                    {"role":"user",
                     "content":f"일기: {diary.contents}\
                        \n이야기 내용에 반영할 키워드: {diary.keyword}\
                        \n주인공 이름: {diary.name}\
                        \n동화:"}]

    request_data = {
        'messages': preset_text,
        'maxTokens': 3300,
        'temperature': 0.75,
        'topK': 0,
        'topP': 0.8,
        'repeatPenalty': 4.0,
        'stopBefore': [],
        'includeAiFilters': True
    }

    return completion_executor.execute(request_data)

# 동화 생성 프롬프트 설정 코드
@app.post("/diaryToStory")
async def diary_to_story(diary: Diary):
    story = create_story(diary)
    title = create_title(story)
    texts = list(map(lambda x: x.strip("\""), story.split("\n\n")))
    return StoryTitleText(title=title, texts=texts)

if __name__ == "__main__":
    uvicorn.run("hyperclova_deploy:app", host="0.0.0.0", port=4000, reload=True)