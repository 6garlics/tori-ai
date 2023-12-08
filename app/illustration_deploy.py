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
# CLOVA_HOST = secrets['clova_host']
# CLOVA_API_KEY = secrets['clova_api_key']
# CLOVA_API_KEY_PRIMARY_VAL = secrets['clova_api_key_primary_val']
# CLOVA_REQUEST_ID = secrets['clova_request_id']

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
    
# class CompletionExecutor:
#     def __init__(self, host, api_key, api_key_primary_val, request_id):
#         self._host = host
#         self._api_key = api_key
#         self._api_key_primary_val = api_key_primary_val
#         self._request_id = request_id

#     def execute(self, completion_request):
#         headers = {
#             'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
#             'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
#             'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
#             'Content-Type': 'application/json; charset=utf-8',
#             'Accept': 'text/event-stream'
#         }
#         try: 
#             with requests.post(self._host + '/testapp/v1/chat-completions/HCX-002',
#                             headers=headers, json=completion_request, stream=True) as r:

#                 results = r.text
#                 result = results.split("\n\n")[-3]
                
#                 data = result.split("\n")[-1][5:]
#                 data = json.loads(data)
#                 content = data['message']['content']
#                 # print(content)
#                 return content
#         except:
#             return None

# completion_executor = CompletionExecutor(
#     host=CLOVA_HOST,
#     api_key=CLOVA_API_KEY,
#     api_key_primary_val=CLOVA_API_KEY_PRIMARY_VAL,
#     request_id=CLOVA_REQUEST_ID
# )
            
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
        'workers': 13,
        'timeout': 600,
        'reload': True
    }
    StandaloneApplication(app, options).run()