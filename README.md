# 토리

세상에 없던 나만의 동화책 **토리**의 AI 개발을 위한 레파지토리입니다.  
**토리**는 아동이 일기를 작성하면 생성형 AI를 통해 만들어진 동화책을 친구들과 공유해 볼 수 있는 플랫폼입니다.

🔗 웹사이트 주소: [https://tori-fairytale.vercel.app/](https://tori-fairytale.vercel.app/) (ID: test, PW: a1234567!)

## ⚒️ System Architecture

### 전체 시스템 구조

![토리 전체 시스템구조 v2](https://github.com/6garlics/tori-ai/assets/69978041/9406890f-3971-44f0-883e-07d7428b7c7a)

### AI 시스템 구조

![tori ai system architecture](https://github.com/6garlics/tori-ai/assets/69978041/2da54178-40f3-4e6b-814d-0368152db500)

### 동화책 생성 흐름
![동화책 생성 흐름](https://github.com/6garlics/tori-ai/assets/69978041/7084f5e9-7dbe-460b-b9c6-ec566b97c442)

## 🏠 Code Structure
> - [app](https://github.com/6garlics/tori-ai/tree/main/app): Directory for deploy fastapi applications  
> - app/illustration_deploy.py: Module for creating an illustration for each paragraph of a story using using DALLE  
> - app/hyperclova_deploy.py: Module for creating a story based on a child's diary using HyperCLOVA X  
> - app/music_deploy.py : Module for creating an music based on a storybook using MusicGen.  
> - [nginx](https://github.com/6garlics/tori-ai/tree/main/nginx) : Directory for nginx  
> - [textual_inversion_project](https://github.com/6garlics/tori-ai/tree/main/textual_inversion_project): Directory for experiments on Stable Diffusion  

## ⚙️ Settings

```bash
git clone https://github.com/6garlics/tori-ai.git
cd tori-ai
pip install -r requirements.txt
```

## 🚀 Deploy

1. Nginx로 Reverse Proxy 설정
- nginx 설치
  ```bash
  sudo apt update
  sudo apt upgrade
  sudo apt autoremove

  sudo apt install nginx
  ```

- nginx.conf 파일 수정
  ```bash
  sudo cp ${PROJECT_ROOT}/nginx/nginx.conf /etc/nginx/nginx.conf
  ```
- nginx 실행
  ```bash
  sudo nginx -t
  sudo systemctl start nginx
  ```

2. `${PROJECT_ROOT}/app/secrets.json` 파일에 credential key, url을 설정한다.

3. gunicorn으로 fastapi 배포 (`${PROJECT_ROOT}/app` 위치에서 실행)
    ```bash
    python illustration_deploy.py
    ```

4. uvicorn으로만 fastapi 배포 (`${PROJECT_ROOT}/app` 위치에서 실행)
    ```bash
    nohup python hyperclova_deploy.py
    ```

    ```bash
    nohup python music_deploy.py
    ```

5. 다시 실행할 때 남아 있는 프로세스 kill
    ```bash
    kill -9 $(lsof -i:${PORT} -t) 2>/dev/null
    ```

## ✅ What I did

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
    - [ ] ~~DreamStudio API~~
- [X] MusicGen 모델로 동화책 배경음악 생성