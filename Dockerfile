FROM westreed/python3.10-ffmpeg

WORKDIR .

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -U pip
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir "discord.py[voice]"

RUN playwright install chromium
RUN playwright install-deps

COPY . .

CMD ["python3", "main.py"]
