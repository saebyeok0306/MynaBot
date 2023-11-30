# discordBot Project

디스코드 서버에 사용하기 위해 개발한 디스코드 봇입니다.<br>
서버 운영에 도움이 되는 명령어가 다수 포함되어 있습니다.

---

## Environment

* IDE : Visual Studio Code
* Language : Python 3.10.8
* Database : SQLite3

---
## Library

* discord.py
* google-api-python-client
* openai
* pillow
* python-dotenv
* tiktoken

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
Naver_Client_Secret=네이버 개발자센터 Secret (Papago)
ChatGPT_Secret=OpenAI Chat GPT Secret (ChatGPT)
Youtube_Secret=Google API Secret (Youtube)
```

### 3. 파이썬 실행

```bash
python main.py
```

---

## How To?

```cmd
!도움말
```

채팅으로 `!도움말`을 입력하면, 사용할 수 있는 명령어를 확인할 수 있습니다.