FROM westreed/python3.10-ffmpeg

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN playwright install

COPY . .

CMD ["python3", "main.py"]
