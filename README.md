# MynaBot Project

디스코드 서버에 사용하기 위해 개발한 디스코드 봇입니다.<br>
서버 운영에 도움이 되는 명령어가 다수 포함되어 있습니다.<br>

현재는 여러 개의 서버에서 운영되고 있으며, 이를 위해 멀티서버를 고려한 코드설계로 전부 변경되었습니다.

---

## Environment

* IDE : Visual Studio Code
* Language : Python 3.10.8
* Database : SQLite3, sqlalchemy

---
## Library

* discord.py
* google-api-python-client
* google-cloud-texttospeech
* langid
* openai
* pillow
* pynacl
* python-dotenv
* pytube
* tiktoken
* yt-dlp (youtube-dl)

---
## Run

### 1. 라이브러리 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

.env 파일을 생성하고, 아래의 내용을 입력합니다.<br>
`Discord_Token2`는 테스트용 봇을 위한 토큰이며, 사용하지 않을 경우 삭제해도 됩니다. (mainTest.py)

```ini
Discord_Token=디스코드봇 토큰 (메인)
Discord_Token2=디스코드봇 토큰 (테스트용봇)
Naver_Client_ID=네이버 개발자센터 ClientID (Papago)
Naver_Client_Secret=네이버 개발자센터 Secret Key (Papago)
OpenAI_Secret=OpenAI Secret Key (ChatGPT, TTS)
Youtube_Secret=Google API Secret Key (Youtube)
GOOGLE_APPLICATION_CREDENTIALS=Google Account (TTS)
```

### 3. ffmpeg 설치

ffmpeg를 설치하고 시스템 환경변수의 path에 등록해야 합니다.

### 4. 봇 실행

```bash
python main.py
python main.py --test # test mode
```

### 5. (선택) YouTube 봇 판정 우회용 쿠키

서버에서 `Sign in to confirm you're not a bot` 오류가 나면, 봇 전용 구글 계정의 youtube.com 쿠키를
Netscape 형식으로 내보내 프로젝트 루트의 `secrets/cookies.txt`에 둡니다. (로컬·서버 동일)<br>
서버에서는 배포 워크플로우가 `secrets/` 폴더를 컨테이너의 `/secrets`에 마운트합니다.
yt-dlp는 실행을 마칠 때 쿠키를 이 파일에 다시 저장하므로 읽기 전용(`:ro`)으로 마운트하지 않으며, 처음 내보낸 쿠키는 따로 백업해 두는 것을 권장합니다.
(레포·이미지에는 포함되지 않으며, 쿠키가 만료되면 파일만 교체한 뒤 봇을 재시작하면 됩니다.)

다른 경로를 쓰려면 `.env`에 `YTDL_COOKIE_FILE=경로`를 지정합니다.

---

## How To?

```cmd
!도움말
```

채팅으로 `!도움말`을 입력하면, 사용할 수 있는 명령어를 확인할 수 있습니다.

## Output

![YouTube Search](https://github.com/westreed/MynaBot/blob/main/src/img/8.png?raw=true)
![YouTube Search](https://github.com/westreed/MynaBot/blob/main/src/img/9.png?raw=true)
![ChatGPT](https://github.com/westreed/MynaBot/blob/main/src/img/10.png?raw=true)