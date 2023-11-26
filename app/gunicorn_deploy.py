from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import json
import io
import uuid
import openai
import boto3
from botocore.exceptions import ClientError
from gunicorn.app.base import BaseApplication
from tempfile import NamedTemporaryFile
from PIL import Image
import requests

app = FastAPI()

with open('secrets.json') as f:
    secrets = json.loads(f.read())

openai.api_key = secrets['openai_api_key']
MODEL = "gpt-3.5-turbo"
FRONTEND_URL = secrets['frontend_url']
BUCKET_NAME = secrets['aws_s3_bucket']
ACCESS_KEY = secrets['aws_access_key']
SECRET_KEY = secrets['aws_secret_key']
LOCATION = secrets['aws_s3_location']
S3_URL = f'https://{BUCKET_NAME}.s3.{LOCATION}.amazonaws.com'
CLOVA_HOST = secrets['clova_host']
CLOVA_API_KEY = secrets['clova_api_key']
CLOVA_API_KEY_PRIMARY_VAL = secrets['clova_api_key_primary_val']
CLOVA_REQUEST_ID = secrets['clova_request_id']

class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application
    
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
            
s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

class Diary(BaseModel):
    name: str = "토리"
    title: Optional[str] = ""
    contents: Optional[str] = "오늘 밤에 자전거를 탔다. 자전거는 처음 탈 때는 좀 중심잡기가 힘들었다. 그러나 재미있었다. 자전거를 잘 타서 엄마, 아빠 산책 갈 때 나도 가야겠다."
    keyword: Optional[str] = "마법"

class StoryTitleText(BaseModel):
    title: str = ""
    texts: List[str] = []

class Cover(BaseModel):
    coverUrl: str = ""

class Paragraph(BaseModel):
    text: str = "" 
    
class Illustration(BaseModel):
    imgUrl: str = ""
    pageNum: int = 0

def create_title(story: str):
    # response = openai.ChatCompletion.create(
    #     model=MODEL,
    #     messages=[
    #         {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
    #          Please make a creative and impressive title of less than five words that expresses the whole story \
    #          and the meaning of the keyword \"{keyword_kor2eng.get(keyword, "마법")}\" well in Korean."""},
    #         {"role": "user", "content": '"""' + story +'"""'},
    #     ],
    #     temperature=0.7,
    # )
    # return response["choices"][0]["message"]["content"].strip("\"")

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

# def make_paragraph_shorter(texts: List[str]):
#     pass


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

def prompt_to_image(prompt: str, style: Optional[str] = "digital art"):
    try:
        response = openai.Image.create(
            prompt=prompt + ", " + style,
            n=1,
            size="1024x1024",
        )
        dalle_url = response['data'][0]['url']
    except:
        return None
    
    object_name = str(uuid.uuid1()) + '.webp'

    file = requests.get(dalle_url).content

    image = Image.open(io.BytesIO(file))

    with NamedTemporaryFile("wb", suffix=".webp", delete=False) as file:
        image.save(file.name, format="webp")
        
        try:
            s3_client.upload_file(
                file.name,
                BUCKET_NAME,
                object_name
            )

        except ClientError as e:
            return None
    image_url = f"{S3_URL}/{object_name}"
    return image_url

# 각 문단별로 이미지 생성 프롬프트로 변환
def text_to_image_prompt(text: str):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "The user will provide you with text delimited by triple quotes. \
             Please convert this text into a prompt \
             that expresses the situation of the text well for the DALL·E model \
             and consists of only one simple sentence and be written in English."},
            {"role": "user", "content": '"""' + text +'"""'},
        ],
        temperature=0.3,
    )
    return response["choices"][0]["message"]["content"] # prompt
    
def prompt_to_one_sentence(prompt: str):
    prompt = prompt.split('.')[0] + "."
    return prompt

@app.post("/textToImage/{pageNum}")
async def text_to_image(pageNum: int, paragraph: Paragraph):
    prompt = text_to_image_prompt(paragraph.text).strip("\"")
    prompt = prompt_to_one_sentence(prompt)
    img_url = prompt_to_image(prompt)
    return Illustration(imgUrl=img_url, pageNum=pageNum)

@app.post("/cover")
async def create_cover(story_title_text: StoryTitleText):
    whole_text = f"title: {story_title_text.title}\n" + "\n".join(story_title_text.texts)
    prompt = text_to_image_prompt(whole_text)
    prompt = prompt_to_one_sentence(prompt)
    cover_url = prompt_to_image(prompt)
    return Cover(coverUrl=cover_url)


if __name__ == "__main__":
    options = {
        'preload_app': True,
        'bind': '%s:%s' % ('0.0.0.0', '8000'),
        'worker_class': 'uvicorn.workers.UvicornWorker',
        # 'post_worker_init': post_worker_init,
        # 'workers': mp.cpu_count() * 2 + 1, # number of GPU worker
        'workers': 9,
        'timeout': 600,
        'reload': True
    }
    StandaloneApplication(app, options).run()