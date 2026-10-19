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
# YouTube의 signature/n challenge를 풀려면 JS 런타임(deno)과 풀이 스크립트(yt-dlp-ejs)가 필요하므로
# default, deno extra를 함께 설치합니다. 없으면 "The page needs to be reloaded." 등으로 재생에 실패합니다.
RUN pip install --no-cache-dir -U "yt-dlp[default,deno]"

# 컨테이너를 시작할 때마다(재시작 워크플로 포함) yt-dlp를 다시 최신으로 올립니다.
# 업데이트에 실패해도 이미지에 설치된 버전으로 봇은 그대로 실행됩니다.
# exec로 실행해야 docker stop 신호가 python 프로세스에 바로 전달됩니다.
CMD ["sh", "-c", "pip install --no-cache-dir -U 'yt-dlp[default,deno]' || echo 'yt-dlp update failed, using installed version'; exec python3 main.py"]
