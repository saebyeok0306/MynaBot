FROM westreed/python3.10-ffmpeg

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -U pip
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir "discord.py[voice]"

RUN playwright install chromium
RUN playwright install-deps

COPY . .

# 유튜브 대응이 자주 갱신되므로, 빌드 캐시와 무관하게 배포할 때마다 yt-dlp를 최신으로 올립니다.
# (COPY . . 뒤에 있어야 코드가 바뀔 때마다 이 레이어가 다시 실행됩니다.)
RUN pip install --no-cache-dir -U yt-dlp

CMD ["python3", "main.py"]
