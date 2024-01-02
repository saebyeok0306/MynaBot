FROM westreed/python3.10-ffmpeg

RUN timedatectl set-timezone Asia/Seoul

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
