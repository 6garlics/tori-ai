# Tori — AI-Powered Personalized Fairytale Generation

**Tori** is an AI system that turns a child’s diary into a personalized fairytale book — complete with story, illustrations, and background music.  
Children can write daily diary entries, transform them into unique storybooks using generative AI, and share them with friends.

🔗 **Live Website**: https://tori-fairytale.vercel.app/  
(ID: `test` / PW: `a1234567!`)
**Note:** The live prototype website is no longer active, but the full backend (story, illustration, music generation) can be run locally using FastAPI.

---

## 🌟 Key Features

✅ Converts children’s diary entries into full fairytale stories  
✅ Generates AI illustrations for every paragraph  
✅ Produces background music aligned with story mood  
✅ Web platform to read and share storybooks  
✅ Entire system deployed on cloud GPU server

---

## ⚒️ System Architecture

### ✅ Overall System

<p align="center">
  <img src="https://github.com/6garlics/tori-ai/assets/69978041/9406890f-3971-44f0-883e-07d7428b7c7a" width="70%">
</p>

### ✅ AI Pipeline

<p align="center">
  <img src="https://github.com/6garlics/tori-ai/assets/69978041/2da54178-40f3-4e6b-814d-0368152db500" width="70%">
</p>

---

## 📘 How a Storybook is Created

<p align="center">
  <img src="https://github.com/6garlics/tori-ai/assets/69978041/7084f5e9-7dbe-460b-b9c6-ec566b97c442" width="70%">
</p>

1. Child writes a diary on the web platform  
2. HyperCLOVA X / ChatGPT generates the full fairytale narrative  
3. Each paragraph is sent to DALL·E to generate illustrations  
4. MusicGen produces a custom BGM based on story context  
5. The final book is displayed on the website and shared

---

## 🏗 Code Structure

```
tori-ai/
├── app/                     # FastAPI services
│   ├── illustration_deploy.py   # DALL·E illustration generation
│   ├── hyperclova_deploy.py     # Story generation (HyperCLOVA X)
│   └── music_deploy.py          # MusicGen BGM generation
├── nginx/                   # Reverse proxy configuration
└── textual_inversion_project/   # SD experiments (LoRA, Textual Inversion)
```

---

## 💻 GPU Server Environment

- **Ubuntu 20.04 LTS (64-bit)**
- **GPU:** Tesla T4
- Nvidia Driver 535.129.03
- CUDA 12.2
- Python 3.8
- FastAPI + Gunicorn + Nginx
- S3 bucket for storing generated images / BGM

---

## ⚙️ Installation

```bash
git clone https://github.com/6garlics/tori-ai.git
cd tori-ai
pip install -r requirements.txt
```

---

## 🚀 Deployment Guide

### ✅ 1. Set up Reverse Proxy (Nginx)

```bash
sudo apt update && sudo apt upgrade
sudo apt autoremove
sudo apt install nginx
sudo cp ${PROJECT_ROOT}/nginx/nginx.conf /etc/nginx/nginx.conf

sudo nginx -t
sudo systemctl start nginx
```

### ✅ 2. Configure Secrets

Create `secrets.json` in `${PROJECT_ROOT}/app` with OpenAI, HyperCLOVA, S3 keys, endpoints, etc.

### ✅ 3. Run FastAPI Services

```bash
# Illustration service
python app/illustration_deploy.py
```

```bash
# Story generation service
nohup python app/hyperclova_deploy.py &
```

```bash
# Music generation service
nohup python app/music_deploy.py &
```

### ✅ 4. Kill active process on port (if needed)

```bash
kill -9 $(lsof -i:${PORT} -t) 2>/dev/null
```

---

## ✅ What I Built

### 🔹 Cloud GPU Server & Backend Deployment
- Provisioned on Tencent Cloud
- Nginx reverse proxy with HTTPS (SSL enabled)
- Gunicorn + FastAPI backend
- Integrated S3 for media storage
- Connected OpenAI API (ChatGPT, DALL·E)
- Integrated HyperCLOVA X API for Korean storytelling

### 🔹 Automated Storybook Generation Pipeline
- Story generation from children’s diaries
- Illustration generation using DALL·E
- BGM generation with MusicGen
- Fully automated workflow from diary → illustrated fairytale → sharable book

### 🔹 Stable Diffusion Experiments (R&D)
- Fine-tuned Stable Diffusion using Textual Inversion
- Fine-tuned Stable Diffusion using LoRA
- (Later deprecated in production in favor of DALL·E)

---

## ✅ Tech Stack

| Component | Technology |
|----------|-------------|
| Backend | FastAPI, Gunicorn, Python |
| Model APIs | HyperCLOVA X, ChatGPT, DALL·E, MusicGen |
| Deployment | Tencent Cloud GPU, Nginx, SSL |
| Storage | S3-compatible object storage |
| Experiments | Stable Diffusion + LoRA + Textual Inversion |

---

## 📌 Future Improvements
- Style-consistent character generation across pages  
- Inference speed optimization on GPU  
- Add multilingual diary → storybook support  
- Real-time audiobook narration

