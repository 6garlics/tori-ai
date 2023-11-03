
1. `${PROJECT_ROOT}/app/secrets.json` 파일에 credential key, url을 설정한다.

2. gunicorn으로 fastapi 배포 (`${PROJECT_ROOT}/app` 위치에서 실행)
    ```bash
    python gunicorn_deploy.py
    ```

3. 다시 실행할 때 남아 있는 프로세스 kill
    ```bash
    kill -9 $(lsof -i:8000 -t) 2>/dev/null
    ```