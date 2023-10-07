# be-my-story-ai

세상에 없던 나만의 동화책 **Be My Story**의 AI 개발을 위한 레파지토리입니다.  
**Be My Story**는 아동이 일기를 작성하면 생성형 AI를 통해 만들어진 e-동화책을 친구들과 공유해 볼 수 있는 플랫폼입니다.

## :white_check_mark: To Do List

### 딥러닝 서버
- FastAPI 로 딥러닝 서버 배포
- S3에 생성된 동화책 일러스트, 동화책 BGM 저장

### 동화책 생성
- 딥러닝 개발 환경 구축
- 동화책 일러스트 일관된 주인공 및 화풍 구현
  - [X] Fine-tune Stable Diffusion using Textual Inversion  
  - [X] Fine-tune Stable Diffusion using LoRA
  - [ ] ~~StyleGAN + FreezeD~~

- MusicGen 모델로 동화책 BGM 생성
-  LLM 모델 프롬프트 가공으로, 일기 기반 동화책 생성
   - [X] ChatGPT