# -*- coding: utf-8 -*-
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
from gunicorn.app.base import BaseApplication
from tempfile import NamedTemporaryFile
from PIL import Image

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

# 나중에 클래스 속성으로 만들기
s3_client = boto3.client(
    's3',
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
    )

origins = [
    FRONTEND_URL,
    S3_URL
]

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# 장르 선택
keyword_kor2eng = {"모험": 'adventure',
                "우주": 'space opera',
                "공룡": 'dinosour fiction',
                "마법": 'magic realism',
                "바다": "ocean",
                "히어로": "hero"
                }

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
    



# 더 나은 방법 찾기 -> keras 실습에서 본 것 같음
def story_template(name, keyword):
    keyword_to_template = {
        "모험": f"어느 날 밤, {name}는 자전거를 타기로 했습니다. \n처음에는 자전거를 타는 게 좀 어려웠지만, 그래도 너무 재미있었어요. \n다음날 엄마와 아빠가 산책을 떠나는 길에 {name}도 자전거를 타고 함께 가기로 했어요. \
                \n\n자전거를 타고 나가는 길은 어둡고 신비로운 숲으로 이어져 있었어요. \n{name}는 조심스럽게 자전거를 몰고 숲을 헤치며 모험을 떠났어요. \n숲 속에는 예쁜 꽃들과 이끼로 덮인 돌들이 있었어요. \n그리고 작은 동물들도 {name}의 모험을 따라 다녔어요. \
                \n\n숲 속을 지나며, {name}는 강을 발견했어요. \n강 물결이 맑고 맑아서 너무 아름다웠어요. \n{name}는 자전거를 한쪽에 두고, 강가에 앉아서 시원한 바람을 맞으며 쉬었어요. \n그리고 작은 배를 보고, {name}도 강에서 모험을 해보고 싶다고 생각했어요. \
                \n\n배에 올라타서 강을 따라 여행을 시작했어요. \n강물을 따라 흘러가면서, {name}는 흥겨운 노래를 불렀어요. \n배 위에서는 새들이 {name}의 노래와 함께 춤을 추며 {name}의 모험을 응원해 주었어요. \
                \n\n하지만 길을 가다보니, 큰 폭포가 나타났어요. \n폭포는 너무나도 높고 거대해서, 지낼 수 없을 것 같았어요. \n하지만 {name}는 포기하지 않았어요. \n자전거를 어깨에 메고 어려운 시련을 겪으면서도 {name}는 결국 폭포를 넘어섰어요. \
                \n\n폭포를 넘어선 뒤, {name}는 큰 호수 앞에 도착했어요. \n호수는 푸른 물결로 가득 차 있었고, \n주변에는 아름다운 꽃들이 피어 있었어요. \n{name}는 호수에서 수영을 하며, 꼬마 물고기들과 재미있는 놀이를 했어요. \
                \n\n모험의 끝에서, {name}는 다시 자전거를 타고 집으로 돌아왔어요. \n엄마와 아빠는 {name}를 반겨주며, {name}의 모험 이야기를 듣기를 기다렸어요. \n{name}는 행복하게 자전거를 내려놓고, 멋진 모험을 마치고 집으로 돌아왔답니다.", 
        # "우주": f"한 참을 연습한 끝에, 저녁에는 {name}는 자전거를 타고 마을을 돌아다녔어요. \n{name}는 처음에는 조금 허덕이지만, 결국은 잘 탈 수 있게 되었어요. \n엄마와 아빠는 {name}가 잘 타는 것을 보고 놀랐어요. \
        #         \n\n자전거 타기는 너무 재미있었고, {name}는 더 많은 모험을 하고 싶었어요. \n그래서 {name}는 우주로 떠나는 우주선을 타기로 결심했어요. \n별들과 함께 모험하고, 색다른 행성들을 탐험하며, 우주를 누비는 것이 {name}의 꿈이었어요. \
        #         \n\n그날 밤, {name}는 잠들기 전에 별들을 보며 꿈을 꾸었어요. 아름다운 우주선이 나타나서 {name}를 초대했어요. {name}는 설레임을 감출 수가 없었어요. 우주선에 올라타서, {name}는 무한한 우주로 향해 모험을 시작했어요. \
        #         \n\n{name}는 처음으로 보는 행성들을 만났어요. \n{name}는 녹색 풀로 덮인 행성에서 꽃들과 만나고, 파란 바다가 펼쳐진 행성에서 아름다운 물고기들을 볼 수 있었어요. \n그리고 또 다른 행성에서는 작은 우주 생물들과 친구가 되어 함께 놀았어요. \
        #         \n\n우주선을 타고 여러 행성들을 방문하면서, {name}는 우주 다른 생물들과 어울리며 새로운 친구들을 사귀었어요. \n함께 놀고 웃으면서, {name}는 매 순간이 행복했어요. \
        #         \n\n하지만 언젠가는 {name}는 집으로 돌아가야 했어요. \n그리고 그녀는 우주선을 타고 지구로 돌아왔어요. \n{name}는 엄마와 아빠에게 모험 이야기를 들려주었고, 그들은 미소 짓더라구요. \
        #         \n\n이후로도 {name}는 언제든 우주 모험을 꿈꿀 수 있었어요. 그리고 {name}는 항상 자전거를 타면서, 다른 행성들을 상상하고 모험을 즐길 수 있었어요.", 
        "우주": f"{name}는 오늘 밤에 자전거를 타기로 했다. {name}는 처음 자전거를 타서 좀 서툴렀지만, 재미있었다고 생각했다. 엄마와 아빠가 산책을 갈 때마다, 하하도 함께 가야겠다고 다짐했어요.\" \
                \n\n{name}는 자전거를 타고 동네를 돌아다니던 중, 하늘에 이상한 빛이 나타났어요. \n그 빛은 화려한 색상으로 빛나며, 하하는 어딘가로 끌려가는 것 같은 기분이 들었어요. \n곧 하하는 빛의 속으로 빨려들어가, 어딘가 신비로운 공간에 도착했어요. \
                \n\n{name}는 놀라움을 금치 못하고 주변을 둘러보았어요. \n그곳은 우주선과 다른 외계 생물들로 가득했어요. \n하하에게 다가온 한 외계인은 밝은 웃음으로 말했어요. \n\"어서와, 우리의 우주 오페라에 온 걸 환영해!\" \
                \n\n\"우주 오페라?\" 하하는 궁금하게 물었어요. \n\"응, 이곳은 우주 세계의 모험과 음악이 어우러진 장소야. 너도 함께 우주선을 타고 환상적인 여행을 떠나보는 건 어때?\" \n외계인은 말했어요. \
                \n\n{name}는 흥미롭게 고개를 끄덕였어요. \n그리고 외계인과 함께 우주선에 올라타, 우주 오페라의 세계로 향하는 여정을 시작했어요. \n그곳에서 하하는 다양한 우주 생물들과 친구가 되었고, 아름다운 우주의 경치를 감상하며 신나는 음악과 춤을 즐겼어요. \
                \n\n{name}는 우주 오페라에서의 모험을 통해 용기와 자신감을 얻었어요. \n그는 자전거를 탈 때의 그 떨리는 기분을 느끼며, 새로운 도전과 모험을 두려워하지 않게 되었어요. \n하하는 우주 오페라를 떠나지만, 그곳에서 배운 것들은 그에게 영원한 추억으로 남았어요. \n그리고 돌아와서는 엄마와 아빠에게 자전거를 타며 용감하게 도전하는 이야기를 들려주었어요.",
        "공룡": f"한가로운 오후, 저녁이 되자마자 {name}는 엄마와 아빠가 산책을 나간다는 소식을 듣고 신이 났어요. 어린이들은 항상 즐거움과 호기심으로 가득 차 있으니까요. \n\"오늘은 저도 엄마와 아빠와 함께 산책을 가야겠어요!\" \n{name}는 흥분한 마음으로 자전거를 타기 시작했어요. \n그런데 처음에는 자전거를 제대로 타는 게 어려웠어요. \n그래도 재미있는 도전이었어요. \
                \n\n처음에는 조금 힘들었지만, {name}는 조심스럽게 자전거에 올라타서 느릿느릿 주차장을 나섰어요. \n산책로에는 잔디와 꽃들이 무성하게 피어있었고, 나무들은 시원한 그늘을 만들어주었어요. \n바람이 부는 소리와 새들의 지저귐이 {name}의 귀를 즐겁게 만들었어요. \
                \n\n자전거를 타면서 {name}는 자연을 느끼고, 시원한 바람을 맞으며 행복감을 느꼈어요. \n그런데, 갑자기 {name}의 시선은 먼 곳으로 향했어요. \n무엇인가 신비로운 것이 보였어요. 그것은 바로 고대의 공룡이었어요! \n공룡들은 오래 전에 살았던 동물들이라고 들었어요. \
                \n\n{name}는 공룡들이 어떤 모습인지 궁금해졌어요. \n그래서 자전거를 멈추고, 조용히 가까이 다가갔어요. \n그러자 공룡들은 놀라지 않고, {name}를 궁금한 눈으로 바라보며 다가와서 인사를 했어요. \n\"안녕하세요, 저희는 공룡 친구들이에요. 여기서 재밌는 이야기를 함께 하고 싶어요. \
                \n\n{name}는 무척 놀랐지만, 너무 신나서 공룡 친구들과 함께 이야기하려고 했어요. \n그들은 제니에게 공룡들의 특별한 힘이란 것을 가르쳐주었어요. \n{name}는 그 힘으로 자전거를 타며 더 높은 곳으로 날아올라갈 수 있었어요. \
                \n\n그 날부터 {name}는 공룡 친구들과 여러 모험을 하면서, 자전거 타기의 재미와 함께 공룡들에 대해 많이 배웠어요. \n어린이들은 {name}와 함께하는 이야기를 통해 공룡들의 생생한 모습과 친구들과의 사이좋은 교류를 즐기며, 새로운 지식을 얻을 수 있었어요.", 
        "마법": f"한때 한 마을에서 살던 아이, {name}는 어느 날 밤, 자전거를 타기로 결심했어요. 처음에는 자전거 타는 것이 어려웠지만, {name}는 재미있기도 했어요. 엄마와 아빠가 산책을 가는 날, {name}도 함께 가보고 싶었습니다. \
                \n\n자전거를 타고 가는 도중, {name}는 한 마을은 물론 더 넓은 세계로도 여행할 수 있다는 것을 알게 되었어요. {name}는 자전거를 탈 때마다 놀라운 일들을 경험하게 되었죠. \
                \n\n어느 날, {name}는 마을 끝자락으로 자전거를 타고 갔어요. 그곳에는 아주 특별한 나무가 있었어요. 그 나무는 어린이들의 소원을 이루어주는 마법 나무였답니다. {name}는 간절히 바라며 소원을 빌었고, 마법 나무는 {name}의 소원을 들어주었어요. \n\n그 이후로 {name}의 삶은 더욱 신기한 일들로 가득 차게 되었어요. 자전거를 타고 지나가는 사람들에게 도움을 주고, 동물들과 대화를 나누는 특별한 능력을 가지게 되었죠. 주변 사람들은 {name}를 마법사처럼 여기며, {name}의 특별한 능력에 놀라움을 금치 못했답니다. \n\n하지만 {name}는 항상 겸손하고 친절한 마음을 가지고 있었어요. {name}는 자전거를 타며 얻은 특별한 능력을 이용하여 도움이 필요한 사람들에게 도움을 주었어요. 누구나 {name}에게 도움을 청하면, 그녀는 마법같은 능력으로 문제를 해결해주었어요. \n\n마을 사람들은 {name}를 따라하기 시작했습니다. 소원을 이루는 마법 나무 앞에서 자전거를 타며 소원을 빌게 되었어요. 그 결과, 마을은 더욱 행복한 곳이 되었어요. 사람들은 서로를 도우며 살아가며 마을은 더욱 번영하게 되었답니다. \n\n자전거를 타는 것만으로도 많은 일들이 일어날 수 있다는 것을 알게 된 {name}는, 자전거를 타는 것을 더욱 즐기게 되었어요. {name}는 항상 자전거를 타고 마법 같은 세계로 여행하며, 자신의 특별한 능력을 활용하여 사람들을 도우며 행복한 일들을 이루어갔습니다.", 
        "바다": f"어느 날 밤, {name}가 자전거를 타기로 했어요. \n처음에는 자전거를 타는 게 좀 어려웠지만 놀라운 경험이었어요. \n{name}는 다음날 엄마와 아빠가 산책을 갈 때 함께 가기로 했어요. \
                \n\n다음 날, 해가 떠오르자마자 {name}는 자전거를 타고 해변으로 향했어요. \n바다를 보러 가기 위해서였죠. \n{name}는 바다를 사랑하고, 바다 속에는 무엇이 있는지 궁금했어요. \
                \n\n바다에 도착하자, {name}는 눈을 휘둘렀어요. \n푸른 바다가 눈에 아름답게 펼쳐져 있었어요. \n파도가 부서지는 소리와 함께 시원한 바다 바람이 불어와서 기분이 좋았어요. \
                \n\n{name}는 생각했어요. \n\"바다에는 어떤 동물들이 살고 있을까요?\" \n그래서 {name}는 바닷속을 둘러보기 시작했어요. \n아주 작은 물고기들이 잔뜩 헤엄치고 있었어요. \n작고 귀여운 해파리들도 있었답니다. \
                \n\n{name}는 바닷속에서 귀여운 해양 생물들을 발견하면서 신나게 놀았어요. \n그리고 {name}가 발견한 건 바로 작은 별모양의 조개껍질이었어요. \n조개껍질을 주머니에 넣고, 소중히 간직하기로 했어요. \
                \n\n바닷속에서 자전거를 타고 놀면서, {name}는 바다에 대해 더 많이 배웠어요. \n바다는 아름다운 동물들과 신비한 보물들로 가득 차 있답니다. \n{name}는 앞으로도 자전거를 타고 바다를 탐험하고 싶어요. \n바다는 언제나 {name}를 기다리고 있을 거예요.",
        "히어로": f"어느 날 밤, {name}는 자전거를 타고 떠났어요. \n처음에는 자전거를 타는 게 조금 어려웠지만, 그래도 재미있었어요. \n그래서 {name}는 엄마와 아빠가 산책을 갈 때 함께 가기로 했어요. \
                \n\n\"엄마, 아빠! 저도 같이 자전거로 산책 가고 싶어요!\" {name}가 말했어요. \
                \n\n\"{name}야, 너도 자전거를 타고 산책을 하고 싶구나? 그렇다면 자전거 타는 법을 잘 배워야 해.\" 엄마가 말했어요. \
                \n\n\"응! 엄마, 아빠가 가르쳐 주세요!\" {name}가 기뻐하며 말했어요. \
                \n\n그러자 엄마와 아빠는 {name}에게 자전거 타는 법을 잘 가르쳐 주었어요. \n{name}는 엄마와 아빠의 도움을 받아 천천히 자전거를 타는 법을 익혔어요. \
                \n\n\"잘했어, {name}야! 이제 우리 가족 모두 함께 자전거로 산책을 할 수 있겠구나!\" 아빠가 칭찬하며 말했어요. \
                \n\n그날 밤, {name}와 가족들은 자전거를 타고 산책을 떠났어요. \n밤하늘에는 반짝이는 별들이 있었고, 바람이 부는 소리가 시원하게 들려왔어요. \n{name}는 자전거를 타고 가족들과 함께 즐거운 시간을 보냈어요. \
                \n\n\"{name}야, 너는 정말 대단해! 자전거를 타는 법을 잘 배워서 우리 가족에게 새로운 경험을 선물해준 거야.\" 엄마가 말했어요. \
                \n\n하하는 자랑스러운 마음으로 웃으며 말했어요. \n\"저도 엄마, 아빠와 함께 자전거를 타고 산책하며 행복한 시간을 보낼 수 있어서 정말 행복해요!\""
    }
    return keyword_to_template.get(keyword, "마법")

class Diary(BaseModel):
    name: str = "주인공" # 프론트 전달: 추가 요청하기
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

def create_title(story: str, keyword: str):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": f"""The user will provide you with text delimited by triple quotes. \
             Please make a creative and impressive title of less than five words that expresses the whole story \
             and the meaning of the keyword \"{keyword_kor2eng.get(keyword, "마법")}\" well in Korean."""},
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
            {"role": "system", "content": f'The user will provide you with text delimited by triple quotes. \
            You change the text into a story that has the meaning of the keyword \"{keyword_kor2eng.get(diary.keyword, "마법")}\" \
            so that it is suitable for children to read and interesting to develop. \
            The name of the main character in this story is \"{diary.name}\". \
            The story should consist of more than six paragraphs consisting of one or two sentences. \
            And please quote the conversation directly and write it in Korean using honorifics.'},
            # assistant role 추가
            {"role": "user", "content": '"""오늘 밤에 자전거를 탔다. 자전거는 처음 탈 때는 좀 중심잡기가 힘들었다. 그러나 재미있었다. 자전거를 잘 타서 엄마, 아빠 산책 갈 때 나도 가야겠다."""'},
            {"role": "assistant", "content": f'{story_template(diary.name, diary.keyword)}'},
            {"role": "user", "content": '"""' + diary.contents +'"""'},
        ],
        temperature=0.75,
        max_tokens=2048
    )
    story = response["choices"][0]["message"]["content"] # story
    title = create_title(story, diary.keyword)
    story.strip("\"\"\"")
    texts = list(map(lambda x: x, story.split("\n\n")))
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

    # 버전 1) dalle api 의 링크 반환
    # return image_url 

    ### image를 S3에 저장 하는 코드 ###
    object_name = str(uuid.uuid1()) + '.webp'
    # 버전 2) 생성된 image를 S3에 저장하여 링크를 반환하는 코드
    
    # 2-1) 저장된 파일을 S3 업로드
    # upload_file_to_s3(file_path, filename)
    
    # 2-2) 읽기 가능한 파일 같은 객체 S3 업로드
    # file: 텍스트가 아닌 바이너리모드로 열린 파일 객체
    file = requests.get(dalle_url).content

#     try:
#         s3_client.upload_fileobj(
#             io.BytesIO(file),
#             BUCKET_NAME,
#             object_name
#     )
#     except ClientError as e:
#         return None

    # s3에 저장
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
    uvicorn.run("gunicorn_deploy:app", host="0.0.0.0", port=8000, reload=True)

# if __name__ == "__main__":
#     options = {
#         'preload_app': True,
#         'bind': '%s:%s' % ('0.0.0.0', '8000'),
#         'worker_class': 'uvicorn.workers.UvicornWorker',
#         # 'post_worker_init': post_worker_init,
#         # 'workers': mp.cpu_count() * 2 + 1, # number of GPU worker
#         'workers': 9,
#         'timeout': 600,
#         'reload': True
#     }
#     StandaloneApplication(app, options).run()
    