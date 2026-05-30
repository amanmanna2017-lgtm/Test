FROM ubuntu:22.04

RUN apt update && apt install -y python3 python3-pip gcc build-essential

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY khalnayak.c .
RUN gcc khalnayak.c -o khalnayak -lpthread -O3 && chmod +x khalnayak

COPY server.py .
COPY bot.py .

CMD python3 server.py & python3 bot.py
