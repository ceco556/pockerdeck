# 🃏 PockerDeck

A lightweight, real-time **Planning Poker** app for agile teams.  
No login, no registration — create a room, share the link, start estimating.

## Features

- **Roles** — room creator is Admin; joiners pick Participant or Viewer
- **Backlog management** — add stories before creating the room; Admin picks the active item; completed items marked Done
- **Estimation types** — Story Points (Fibonacci), T-shirt sizes, Hours, or fully Custom card sets
- Real-time voting via WebSockets — all participants see updates live
- Votes stay hidden until revealed — prevents anchoring bias
- Results panel shows average, min, and max after reveal
- New Round resets votes without losing the active story or backlog
- Admin can kick users and rename them
- Copy Link button — shareable link is always clean
- Fully Dockerised — multi-arch image (`linux/amd64` + `linux/arm64`)

## Quick start

```bash
git clone https://github.com/byteavanta/pockerdeck.git
cd pockerdeck
docker compose up -d --build
```

Visit [http://localhost:8000](http://localhost:8000).

## Docker Hub

```bash
docker run -d -p 8000:8000 --restart unless-stopped ceco556/pockerdeck:latest
```

## Deploy on a server

```yaml
services:
  web:
    image: ceco556/pockerdeck:latest
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

## Documentation

Full docs at **https://byteavanta.github.io/pockerdeck-doc/**
