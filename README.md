# 토리

세상에 없던 나만의 동화책 **토리**의 AI 개발을 위한 레파지토리입니다.  
**토리**는 아동이 일기를 작성하면 생성형 AI를 통해 만들어진 동화책을 친구들과 공유해 볼 수 있는 플랫폼입니다.

## ⚒️ 시스템 구조
### 전체 시스템 구조

![토리 전체 시스템구조 v2](https://github.com/6garlics/tori-ai/assets/69978041/9406890f-3971-44f0-883e-07d7428b7c7a)

### AI 시스템 구조

![tori ai system architecture](https://github.com/6garlics/tori-ai/assets/69978041/2da54178-40f3-4e6b-814d-0368152db500)

### 동화책 생성 흐름
![동화책 생성 흐름](https://github.com/6garlics/tori-ai/assets/69978041/7084f5e9-7dbe-460b-b9c6-ec566b97c442)


## ✅ To Do List

### 딥러닝 서버

- [X] Tencent Cloud 배포
  - [x] Nginx (리버스 프록시 웹서버)
  - [x] SSL 적용
  - [x] Gunicorn (WSGI)
  - [x] FastAPI
  - [x] S3 연결 (동화책 삽화 및 BGM 저장)
  - [X] OpenAI API 연결
  - [X] Naver HyperClova X API 연결

### 동화책 생성
  
- [X] GPU 서버 구축
- [X] 동화책 이야기 생성
  - [X] ChatGPT API
  - [X] HyperCLOVA API
- [X] 동화책 삽화 생성
  - [X] DALLE OpenAI API
  - [ ] ~~Stable Diffusion (취소)~~
    - [X] Fine-tune Stable Diffusion using Textual Inversion
    - [X] Fine-tune Stable Diffusion using LoRA
    - [ ] DreamStudio API
- [X] MusicGen 모델로 동화책 배경음악 생성

## ⚙️ Settings

```bash
git clone https://github.com/6garlics/tori-ai.git
cd tori-ai
pip install -r requirements.txt
```