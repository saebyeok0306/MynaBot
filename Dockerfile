FROM python:3.10

RUN apt-get update && \
    apt-get install -y ffmpeg

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]
