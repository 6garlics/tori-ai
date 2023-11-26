# be-my-story-ai

세상에 없던 나만의 동화책 **Be My Story**의 AI 개발을 위한 레파지토리입니다.  
**Be My Story**는 아동이 일기를 작성하면 생성형 AI를 통해 만들어진 e-동화책을 친구들과 공유해 볼 수 있는 플랫폼입니다.

## :white_check_mark: To Do List

### 딥러닝 서버

- Tencent Cloud 배포
  - [x] Nginx (리버스 프록시 웹서버)
  - [x] Gunicorn (WSGI)
  - [x] FastAPI
  - [x] S3 (동화책 삽화 및 BGM 저장)
  - [x] SSL 적용

### 동화책 생성
- 딥러닝 개발 환경 구축
  
- [ ] 동화책 이야기 생성
   - [X] ChatGPT API
   - [X] HyperCLOVA API
- 동화책 삽화 생성
  - [ ] Stable Diffusion
    - [X] Fine-tune Stable Diffusion using Textual Inversion
    - [X] Fine-tune Stable Diffusion using LoRA
    - [ ] DreamStudio API
  - [X] DALLE OpenAI API
- [X] MusicGen 모델로 동화책 BGM 생성


# Settings

```bash
git clone https://github.com/6garlics/be-my-story-ai.git
cd be-my-story-ai
pip install -r requirements.txt
```