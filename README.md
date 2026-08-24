# Network Security Analysis

A home-network traffic pipeline: [Zeek](https://zeek.org/) parses raw packet
captures into structured logs, a watcher ingests them into Postgres, and a
small Django app serves a dashboard for browsing and filtering connections
(including a live-updating feed).

## How it fits together

```
tcpdump  ->  captures/*.pcap  ->  Zeek (docker)  ->  zeek_logs/*.log
                                                          |
                                                          v
                                          scripts/watch_captures.py
                                          scripts/ingest_zeek_logs.py
                                                          |
                                                          v
                                                     Postgres  ->  Django UI
```

- `Makefile` — `make capture` runs `tcpdump` in 60s rotating segments into
  `captures/`; `make watch` runs the ingestion watcher.
- `docker-compose.zeek.yaml` — runs Zeek against a pcap, writing logs to
  `zeek_logs/`.
- `scripts/watch_captures.py` — watches `captures/` for new pcaps, runs them
  through Zeek, and moves them to `processed/` or `error/`.
- `scripts/ingest_zeek_logs.py` — parses `zeek_logs/conn.log` into the
  `ZeekConnLog` Django model.
- `log_entries/` — Django app: models, views, and templates for the
  connection log dashboard (`/logs/`, `/logs/live/`, `/logs/feed/`).

The `zeek_logs/` and `captures/` sample data checked in here is anonymized
(hostnames/MACs replaced) home-network traffic, kept only to illustrate the
log formats and dashboard.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # fill in DB credentials and SECRET_KEY

docker compose up -d db
python manage.py migrate
python manage.py runserver
```

Set `DEBUG=True` in `.env` for local development; it defaults to `False`.

To process captures:

```bash
docker compose -f docker-compose.zeek.yaml run zeek
python scripts/ingest_zeek_logs.py
```
