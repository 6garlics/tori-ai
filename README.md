# be-my-story-ai

- Development Environment
    - CPU i7-770HQ, RAM 16GB  
    - GeForce GTX 1060 Mobile (VRAM 6GB)
    - Ubuntu 20.04  
    - Nvidia Driver 515.43.04  
    - CUDA 11.7  
    - Cudnn 8.6.0

## 학습 이미지 데이터 만들기
### Settings

```bash
conda create -n data-env python==3.9
conda activate data-env
conda install -c conda-forge selenium
pip install webdriver_manager
pip install bs4
```

```bash
export KEYWORD='marnie'
```

### Crawling

```bash
python utils/crawl.py -k ${KEYWORD}
```

### Resizing

```bash
python utils/resize.py -k ${KEYWORD}
```


## Fine-tune Stable Diffusion using Texture Inversion

### Settings
1. python, 추가 라이브러리 설치
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt install -y python3.10 python3-pip python3.10-venv
sudo update-alternatives --install /usr/local/bin/python python /usr/bin/python3.10 3

sudo apt update && sudo apt install -y libglib2.0-0 libgl1-mesa-glx

```
2. [Invoke-ai releases v2.3.5](https://github.com/invoke-ai/InvokeAI/releases/tag/v2.3.5)를 다운 후 압축해제 (설치 당시 가장 최신 버전)

3. install.sh 실행 -> Configuration 설정 -> Model 다운
```bash
bash install.sh
```

### Training
1. 학습 데이터
```bash
mkdir -p textual-inversion-training-data/${KEYWORD}
```
`textual-inversion-training-data/${KEYWORD}` 디렉토리 아래에 학습하고자하는 이미지 3~5개를 위치시킨다.

2. Run textual inversion training


```bash
bash invoke.sh
```
`3: Run textual inversion training`를 선택

- Configuration
    - Model: stable-diffusion-1.5
    - Initializer: *
    - Triger Term: `${KEYWORD}`
    - Learnable property: 'style'
    - Number of training epochs: 250
    - Max Training Steps: 2500
    - Batch Size: 1
    - Gradient Accumulation Steps: 4
    - Learning Rate: 0.0005
    - Learning Rate Schduler: constant
    - Use xformers acceleration

## Inference

```bash
bash invoke.sh
```
1. `2: Command-line interface`를 선택
2. 프롬프트 입력
3. `outputs` 디렉토리 아래에 생성된 이미지 확인