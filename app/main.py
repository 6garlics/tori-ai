from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import json
import io
import uuid
import requests
import openai
import boto3
from botocore.exceptions import ClientError
from fastapi.middleware.cors import CORSMiddleware
from tempfile import NamedTemporaryFile
import torch
import torchaudio
from audiocraft.models import MusicGen
"""

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

genre_mapping = {"모험": 'adventure',
                "성장": 'growth',
                "판타지": 'fantasy',
origins = [
    FRONTEND_URL,
    S3_URL
]
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
                # "코미디": 'comedy',
                # "우화": 'fable',
                "SF": 'SF',
                "추리": 'mystery',
                # "드라마": 'drama'
                }
# 장르 어떤 것 
  
class Diary(BaseModel):
    title: Optional[str] = ""
    contents: Optional[str] = ""
    genre: Optional[str] = ""

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


# 나중에 클래스 속성으로 만들기
s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
    )

# def upload_file_to_s3(file_path, object_name): # file_path ?
#     try:
#         s3_client.upload_file(file_path, BUCKET_NAME, object_name)
#     except ClientError as e:
#         return None
    
#     image_url = f'{S3_URL}/{object_name}'
#     return image_url

def create_title(story: str, genre: str):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
             Please make a creative title of about five words that expresses the whole story \
             and {genre_mapping.get(genre, "판타지")} genre well in Korean."""},
            {"role": "user", "content": '"""' + story +'"""'},
        ],
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"].strip("\"")

# 동화 생성 프롬프트 설정 코드
@app.post("/diaryToStory")
async def diary_to_story(diary: Diary):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
            Please change this diary into a story of {genre_mapping.get(diary.genre, "판타지")} genre \
            so that it is suitable for children to read and interesting to develop. \
            The main character of this story is a girl Jenny. \
            The story consists of more than six paragraphs consisting of about two sentences.
            And please write it in Korean using honorifics."""},
            {"role": "user", "content": '"""' + diary.contents +'"""'},
        ],
        temperature=0.75,
    )
    story = response["choices"][0]["message"]["content"] # story
    title = create_title(story, diary.genre)
    texts = list(map(lambda x: x.strip("\""), story.split("\n\n")))
    return StoryText(title=title, texts=texts)

def prompt_to_image(prompt: str, style: Optional[str] = "digital art"):
    try:
        response = openai.Image.create(
            prompt=prompt + ", " + style,
            n=1,
            size="1024x1024"
        )
        dalle_url = response['data'][0]['url']
    except:
        return None

    # 버전 1) dalle api 의 링크 반환
    # return image_url 

    ### image를 S3에 저장 하는 코드 ###
    object_name = str(uuid.uuid1()) + '.jpg'
    # 버전 2) 생성된 image를 S3에 저장하여 링크를 반환하는 코드
    
    # 2-1) 저장된 파일을 S3 업로드
    # upload_file_to_s3(file_path, filename)
    
    # 2-2) 읽기 가능한 파일 같은 객체 S3 업로드
    # file: 텍스트가 아닌 바이너리모드로 열린 파일 객체
    file = requests.get(dalle_url).content

    try:
        s3_client.upload_fileobj(
            io.BytesIO(file),
            BUCKET_NAME,
            object_name
    )
    except ClientError as e:
        return None
    
    image_url = f"{S3_URL}/{object_name}"
    return image_url

# 각 문단별로 이미지 생성 프롬프트로 변환
def text_to_prompt(text: str):
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
    prompt = text_to_prompt(paragraph.text).strip("\"")
    prompt = prompt_to_one_sentence(prompt)
    img_url = prompt_to_image(prompt)
    return Illustration(imgUrl=img_url, pageNum=pageNum)

@app.post("/cover")
async def create_cover(story_text: StoryText):
    whole_text = f"title: {story_text.title}\n" + "\n".join(story_text.texts)
    prompt = text_to_prompt(whole_text)
    prompt = prompt_to_one_sentence(prompt)
    cover_url = prompt_to_image(prompt)
    return Cover(coverUrl=cover_url)


# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)