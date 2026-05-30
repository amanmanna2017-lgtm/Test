FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    gcc \
    build-essential \
    libc6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY khalnayak.c .
RUN gcc khalnayak.c -o khalnayak -lpthread -O3 -Wall 2>&1 || \
    echo "GCC Output:" && cat khalnayak.c

RUN chmod +x khalnayak 2>/dev/null || true

COPY server.py .
COPY bot.py .

EXPOSE 8080

CMD python3 server.py & sleep 5 && python3 bot.py
