# 1. 베이스 이미지 선택
FROM ubuntu:22.04

# 2. 환경 변수 설정 (APT 설치 시 불필요한 질의 방지)
ENV DEBIAN_FRONTEND=noninteractive

# 3. 시스템 업데이트 및 필요한 패키지 설치 (위에서 실행해본 명령어)
#    설치 후 apt 캐시를 제거하여 이미지 크기 최적화
RUN apt-get update && \
    apt-get install -y python3 python3-pip curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# 4. Jupyter Notebook 및 관련 라이브러리 설치 (위에서 실행해본 명령어)
RUN pip3 install jupyter numpy pandas matplotlib

# 5. 작업 디렉토리 설정 (컨테이너 내부의 기본 작업 경로)
WORKDIR /app

# 6. Jupyter Notebook이 사용할 포트 노출
EXPOSE 8888

# 7. 컨테이너 시작 시 실행될 명령어
CMD ["jupyter", "notebook", "--allow-root", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--NotebookApp.token=''"]