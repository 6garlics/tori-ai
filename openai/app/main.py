from fastapi import FastAPI
import openai
from pydantic import BaseModel
from typing import Optional, List
import json
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

with open('secrets.json') as f:
    secrets = json.loads(f.read())
openai.api_key = secrets['openai_api_key']
MODEL = "gpt-3.5-turbo"

genre_mapping = {"모험": 'adventure',
                "성장": 'growth',
                "판타지": 'fantasy',
                "코미디": 'comedy',
                "우화": 'fable',
                "SF": 'SF',
                "추리": 'mystery',
                "드라마": 'drama'
                }
  
class Diary(BaseModel):
    id: Optional[int] = 0
    subject: Optional[str] = "" # Optional value
    contents: Optional[str] = ""
    story_type: Optional[str] = ""
    date: Optional[str] = "2023-07-00"

class Storybook(BaseModel):
    subject: str = ""
    paragraphs: List[str] = []
    img_urls: List[str] = []
    story_type: Optional[str] = ""
    date: str = ""
    
# 동화 생성 프롬프트 설정 코드
def diary_to_story(diary: Diary):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
            Please change this diary into a story of {genre_mapping.get(diary.story_type, "판타지")} genre \
            so that it is suitable for children to read and interesting to develop. \
            The main character of this story is a girl Jenny. \
            A fairy tale should have no more than four paragraphs and please write it in Korean using honorifics."""},
            {"role": "user", "content": '"""' + diary.contents +'"""'},
        ],
        temperature=0.75,
    )
    return response["choices"][0]["message"]["content"] # story

# 각 문단별로 이미지 생성 프롬프트로 변환
def paragraph_to_prompt(paragraph: str):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "The user will provide you with text delimited by triple quotes. \
             Please convert this text into a prompt \
             that expresses the situation of the text well for the DALL·E model \
             and consists of only one simple sentence and be written in English."},
            {"role": "user", "content": '"""' + paragraph +'"""'},
        ],
        temperature=0.3,
    )
    return response["choices"][0]["message"]["content"] # prompt
    
# def change_prompt_character(prompt: str):
#     response = openai.ChatCompletion.create(
#         model=MODEL,
#         messages=[
#             {"role": "system", "content": "The user will provide you with text delimited by triple quotes. \
#              Please change the main character of this prompt to a young girl"},
#             {"role": "user", "content": '"""' + prompt +'"""'},
#         ],
#         temperature=0,
#     )
#     return response["choices"][0]["message"]["content"] # prompt

def prompt_to_image(prompt: str, style: Optional[str] = "digital art"):
    # print("style:", style)
    response = openai.Image.create(
        prompt=prompt + ", " + style,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
    return image_url

def create_subject(story: str, story_type: str):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
             Please make a creative title that expresses the whole story \
             and {genre_mapping.get(story_type, "판타지")} genre well in Korean."""},
            {"role": "user", "content": '"""' + story +'"""'},
        ],
        temperature=0.7,
    )
    return response["choices"][0]["message"]["content"] # prompt
    # return "new subject"

def prompt_to_one_sentence(prompt: str):
    prompt = prompt.split('.')[0] + "."
    return prompt

@app.post("/storybook")
async def diary_to_storybook(diary: Diary):
    story = diary_to_story(diary)
    paragraphs = story.strip("\"").split("\n\n")
    subject = create_subject(story, diary.story_type)

    img_urls = []
    for paragraph in paragraphs:
        # print("paragraph: ", paragraph)
        prompt = paragraph_to_prompt(paragraph).strip("\"")
        # print("prompt 1: ", prompt)
        # prompt = change_prompt_character(prompt).strip("\"")
        # print("prompt 2: ", prompt)
        prompt = prompt_to_one_sentence(prompt)
        # print("prompt 2: ", prompt)

        img_url = prompt_to_image(prompt)
        img_urls.append(img_url)
    
    storybook = {"subject": subject,
                 "paragraphs": paragraphs, 
                 "img_urls": img_urls,
                 "story_type": diary.story_type,
                 "date": diary.date, 
                 }
    return Storybook(**storybook)