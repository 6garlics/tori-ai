from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Optional, List
import json
import uuid
import openai
import boto3
from botocore.exceptions import ClientError
from tempfile import NamedTemporaryFile
import torch
import torchaudio
import gc
from audiocraft.models import MusicGen

model = MusicGen.get_pretrained('facebook/musicgen-small', device=torch.device("cuda"))
model.set_generation_params(
    use_sampling=True,
    top_k=250,
    duration=30
)

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

app = FastAPI()

class StoryText(BaseModel):
    texts: List[str] = []

class Music(BaseModel):
    musicUrl: str = ""
    
def story_to_music_prompt(story):
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "The user will provide you with text delimited by triple quotes. \
            Please convert this text into a prompt \
            which composes music that explains and expresses the overall atmosphere and message of the text well \
            and contains which instruments to use, musical genre and rhythm. \
            The prompt should consist of only one simple sentence and be written in English."},
            {"role": "user", "content": '"""' + story +'"""'},
        ],
        temperature=0.75,
        max_tokens=2048
    )
    return response["choices"][0]["message"]["content"] # prompt

def prompt_to_music(prompt, sample_rate=32000):
    object_name = str(uuid.uuid1()) + '.wav'
    
    with torch.no_grad():
        # wav 생성
        outputs = model.generate(
            descriptions=[
                prompt
            ],
            progress=True, return_tokens=True
        )
        wav = outputs[0][0].detach().cpu().float()
        
        assert wav.dtype.is_floating_point, "wav is not floating point"
        if wav.dim() == 1:
            wav = wav[None]
        elif wav.dim() > 2:
            raise ValueError("Input wav should be at most 2 dimension.")
        assert wav.isfinite().all()
        
        # s3에 저장
        with NamedTemporaryFile("wb", suffix=".wav", delete=False) as file:
            torchaudio.save(file.name, wav, sample_rate=sample_rate, format='wav')
            try:
                s3_client.upload_file(
                    file.name,
                    BUCKET_NAME,
                    object_name
                )
            except ClientError as e:
                return None
    
    del outputs, wav
    gc.collect()
    torch.cuda.empty_cache()
    
    music_url = f"{S3_URL}/{object_name}"
    return music_url

@app.post("/music")
async def story_to_music(story_text: StoryText):
    texts = "\n".join(story_text.texts)
    prompt = story_to_music_prompt(texts)
    music_url = prompt_to_music(prompt)
    return Music(musicUrl=music_url)

if __name__ == "__main__":
    uvicorn.run("uvicorn_deploy:app", host="0.0.0.0", port=5000, reload=True)