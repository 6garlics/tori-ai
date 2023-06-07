import os
import sys
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from bs4 import BeautifulSoup
import argparse

# 크롬 드라이버 설정
# (크롤링할 때 웹 페이지 띄우지 않음, gpu 사용 안함, 한글 지원, user-agent 헤더 추가)
def set_chrome_driver():
    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

parser = argparse.ArgumentParser()
parser.add_argument('--key', '-k', required=True, help='작품 키워드')
args = parser.parse_args()

keyword = args.key
max_images = 50

# 프로젝트에 미리 생성해놓은 crawled_img폴더 안에 하위 폴더 생성
path = 'data/crawled_data/'+keyword
try:
    if not os.path.exists(path):
        os.makedirs(path)
    else:
        print('이전에 같은 작품으로 다운로드한 폴더가 존재합니다.')
except OSError:
    print ('os error')
    sys.exit(0)

image_count = 0 # 추출 시도 이미지 수
driver = set_chrome_driver()

for i in range(1, max_images+1):
    #웹 페이지 접근 후 1초동안 로드를 기다림
    driver.get('https://www.ghibli.jp/works/'+keyword+'/#frame&gid=1&pid='+str(i))
    sleep(1)

    #크롤링이 가능하도록 html코드 가공
    html = driver.page_source
    soup = BeautifulSoup(html,'html.parser')

    # imgs = soup.select('div.flex_grid.credits.search_results img') #요소 선택
    images = soup.select('img.pswp__img') #요소 선택
    # print("images", images)
    # 5번 제목에서 설명함
    for img in images:

        
        src = img.get('src')
        
        filename = src.split('/')[-1] #이미지 경로에서 날짜 부분뒤의 순 파일명만 추출
        save_url = path+'/'+filename #저장 경로 결정
        
        if os.path.exists(save_url): continue
        image_count+=1
        print(image_count)
        print("가져오는 경로:", src)
        print("이미지 파일명:", filename)
        print("저장되는 경로:", save_url)

        #파일 저장
        #user-agent 헤더를 가지고 있어야 접근 허용하는 사이트도 있을 수 있음(pixabay가 이에 해당)
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            img_url = urllib.request.urlopen(req).read() #웹 페이지 상의 이미지를 불러옴
            with open(save_url,"wb") as f: #디렉토리 오픈
                f.write(img_url) #파일 저장
        except urllib.error.HTTPError:
            print('에러')
            sys.exit(0)

if image_count == max_images:
    print('성공')
else:
    print(f'실패: {max_images-image_count}')