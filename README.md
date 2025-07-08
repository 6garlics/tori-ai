# Tori

**Tori** is a repository for building an AI system that creates personalized fairytale books like never before.  
Tori is a platform where children can write diaries and generate unique storybooks using generative AI, which they can then share with friends.

🔗 Website Address: [https://tori-fairytale.vercel.app/](https://tori-fairytale.vercel.app/)  
(ID: test, PW: a1234567!)

## ⚒️ System Architecture

### ⛏️ Overall System Architecture

![Tori Overall System Architecture v2](https://github.com/6garlics/tori-ai/assets/69978041/9406890f-3971-44f0-883e-07d7428b7c7a)

### 🔨 AI System Architecture

![Tori AI System Architecture](https://github.com/6garlics/tori-ai/assets/69978041/2da54178-40f3-4e6b-814d-0368152db500)

## 💫 How a Story Book is Created

![Storybook Generation Flow](https://github.com/6garlics/tori-ai/assets/69978041/7084f5e9-7dbe-460b-b9c6-ec566b97c442)

## 🏠 Code Structure

> - [app](https://github.com/6garlics/tori-ai/tree/main/app): Directory for FastAPI applications  
>   - [app/illustration_deploy.py](https://github.com/6garlics/tori-ai/blob/main/app/illustration_deploy.py): Generates illustrations for each paragraph using DALL·E  
>   - [app/hyperclova_deploy.py](https://github.com/6garlics/tori-ai/blob/main/app/hyperclova_deploy.py): Generates stories from children's diaries using HyperCLOVA X  
>   - [app/music_deploy.py](https://github.com/6garlics/tori-ai/blob/main/app/music_deploy.py): Generates background music from the storybook using MusicGen  
> - [nginx](https://github.com/6garlics/tori-ai/tree/main/nginx): Nginx configuration files  
> - [textual_inversion_project](https://github.com/6garlics/tori-ai/tree/main/textual_inversion_project): Experiments with Stable Diffusion

## 💻 Server

> Ubuntu Server 20.04 LTS 64bit  
> GPU: Tesla T4  
> Nvidia Driver 535.129.03  
> CUDA 12.2  
> Python 3.8  

## ⚙️ Setup

```bash
git clone https://github.com/6garlics/tori-ai.git
cd tori-ai
pip install -r requirements.txt
```

## 🚀 Deploy

1. Set up Reverse Proxy with Nginx
- Install Nginx:
  ```bash
  sudo apt update
  sudo apt upgrade
  sudo apt autoremove

  sudo apt install nginx
  ```

- Replace nginx.conf:
  ```bash
  sudo cp ${PROJECT_ROOT}/nginx/nginx.conf /etc/nginx/nginx.conf
  ```
- Run Nginx:
  ```bash
  sudo nginx -t
  sudo systemctl start nginx
  ```

2. `Configure `secrets.json` with credentials and URLs in `${PROJECT_ROOT}/app`.

3. Deploy FastAPI via Gunicorn (run from `${PROJECT_ROOT}/app`):
    ```bash
    python illustration_deploy.py
    ```

4. Deploy FastAPI via Uvicorn:
    ```bash
    nohup python hyperclova_deploy.py
    ```

    ```bash
    nohup python music_deploy.py
    ```

5. To kill a running process on the same port:
    ```bash
    kill -9 $(lsof -i:${PORT} -t) 2>/dev/null
    ```

## ✅ What I did

### Deep Learning Server

- [X] Deployed on Tencent Cloud
  - [x] Nginx (Reverse Proxy Web Server)
  - [x] SSL Configuration
  - [x] Gunicorn (WSGI)
  - [x] FastAPI
  - [x] S3 Integration (store storybook illustrations and BGM)
  - [X] Integrated OpenAI API
  - [X] Integrated Naver HyperCLOVA X API

### Automated Storybook Generation
  
- [X] Built GPU Server
- [X] Story Generation
  - [X] ChatGPT API
  - [X] HyperCLOVA API
- [X] Illustration Generation
  - [X] DALLE OpenAI API
  - [ ] ~~Stable Diffusion (취소)~~
    - [X] Fine-tune Stable Diffusion using Textual Inversion
    - [X] Fine-tune Stable Diffusion using LoRA
    - [ ] ~~DreamStudio API~~
- [X] Generated background music using MusicGen
