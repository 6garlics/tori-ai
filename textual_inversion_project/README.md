
## :pencil2: Contents

> [학습 이미지 데이터 만들기](#woman_technologist-학습-이미지-데이터-만들기)  
> [Fine-tune Stable Diffusion using Texture Inversion](#woman_technologist-fine-tune-stable-diffusion-using-texture-inversion)  
> [Inference Stable Diffusion with embeddings](#woman_technologist-inference-stable-diffusion-with-embeddings)

## :computer: Development Environment
    - CPU i7-770HQ, RAM 16GB  
    - GeForce GTX 1060 Mobile (VRAM 6GB)
    - Ubuntu 20.04  
    - Nvidia Driver 515.43.04  
    - CUDA 11.7  
    - Cudnn 8.6.0

## :woman_technologist: 학습 이미지 데이터 만들기
### Settings

1. 가상환경 만들기
    ```bash
    conda create -n data-env python==3.9
    conda activate data-env
    ```
2. 필요한 패키지 설치
    ```bash
    conda install -c conda-forge selenium
    pip install webdriver_manager
    pip install bs4
    ```
3. 이미지 키워드 환경 변수 설정
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


## :woman_technologist: Fine-tune Stable Diffusion using Texture Inversion

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
   ```bash
   mkdir -p ${PROJECT_ROOT}/textual_inversion/training
   
   wget https://github.com/invoke-ai/InvokeAI/releases/download/v2.3.5/InvokeAI-installer-v2.3.5.zip
   unzip -d invokeai InvokeAI-installer-v2.3.5.zip
   ```

3. install.sh 실행 -> Configuration 설정 -> Model 다운
    ```bash
    bash install.sh
    ```

### Training
1. 학습 데이터
    ```bash
    mkdir -p textual-inversion-training-data/${KEYWORD}
    ```
    `textual-inversion-training-data/${KEYWORD}` 디렉토리 아래에 학습하고자 하는 이미지 3~5개를 위치시킨다.

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

## :woman_technologist: Inference Stable Diffusion with embeddings

### Method 1. InvokeAI 이용
1. Prompt 열기
   ```bash
    bash invoke.sh
    ```
    `2: Command-line interface`를 선택

2. Prompt 입력
3. `outputs` 디렉토리 아래에 생성된 이미지 확인

### Method 2. Colab 이용

1. 해당 레포지토리의 `textual_inversion/inference` 디렉토리를 구글 드라이브에 업로드
2. [구글 공유 드라이브](https://drive.google.com/drive/folders/1j8NN3yn6BziBPT_h-OYD5H48ao4MoqKt?usp=sharing)에서 pretrained model과  embedding 다운 후, 각각 `textual_inversion/models/ldm/stable-diffusion-v1/model.ckpt`, `textual_inversion/embeddings/${KEYWORD}/learned_embeds.bin`에 위치시키기
3. `inference_stable_diffusion_with_embeddings.ipynb` 실행
4. `textual_inversion/outputs` 디렉토리 아래에 생성된 이미지 확인


