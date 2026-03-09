# 🃏 PockerDeck

A lightweight, real-time **Planning Poker** app for agile teams.  
No login, no registration — create a room, share the link, start estimating.

## Features

- Create a room instantly with a shareable link
- Real-time voting via WebSockets — all participants see updates live
- Cards: `3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 30+, ?`
- Votes stay hidden until the host reveals them
- Results panel shows average, min, and max after reveal
- "New Round" resets all votes for everyone
- Optional story/task description shared across the room
- Fully Dockerised — runs anywhere

## Run locally

```bash
git clone https://github.com/your-username/pockerdeck.git
cd pockerdeck
docker compose up -d --build
```

Visit [http://localhost:8000](http://localhost:8000).

## Deploy on a server

```yaml
services:
  web:
    image: your-dockerhub-username/pockerdeck:latest
    ports:
      - "8000:8000"
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

The app will be available at `http://<YOUR_SERVER_IP>:8000`.
