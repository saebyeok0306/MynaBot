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

### 4. 파이썬 실행

```bash
python main.py
```

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