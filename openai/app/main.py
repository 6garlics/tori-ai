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
    title: Optional[str] = ""
    contents: Optional[str] = ""
    genre: Optional[str] = ""
class StoryText(BaseModel):
    title: str = ""
    texts: List[str] = []

class Cover(BaseModel):
    coverUrl: str = ""

class Paragraph(BaseModel):
    text: str = ""
class Illustration(BaseModel):
    imgUrl: str = ""

def create_title(story: str, genre: str):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
             Please make a creative title that expresses the whole story \
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
            A fairy tale should have no more than four paragraphs and please write it in Korean using honorifics."""},
            {"role": "user", "content": '"""' + diary.contents +'"""'},
        ],
        temperature=0.75,
    )
    story = response["choices"][0]["message"]["content"] # story
    title = create_title(story, diary.genre) # COVER
    texts = story.strip("\"").split("\n\n")
    return StoryText(title=title, texts=texts)


######################

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
    response = openai.Image.create(
        prompt=prompt + ", " + style,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']
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

@app.post("/textToImage")
async def text_to_image(paragraph: Paragraph):
    prompt = text_to_prompt(paragraph.text).strip("\"")
    prompt = prompt_to_one_sentence(prompt)
    img_url = prompt_to_image(prompt)
    return Illustration(imgUrl=img_url)

@app.post("/cover")
async def create_cover(story_text: StoryText):

    whole_text = f"title: {story_text.title}\n" + "\n".join(story_text.texts)
    # print("whole text:", whole_text)
    prompt = text_to_prompt(whole_text)
    # print("prompt 1:", prompt)
    prompt = prompt_to_one_sentence(prompt)
    # print("prompt 2:", prompt)
    cover_url = prompt_to_image(prompt)
    # print("cover url:", cover_url)
    return Cover(coverUrl=cover_url)