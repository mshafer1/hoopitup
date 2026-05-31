
# Hoop It Up

Hoop It Up is a progressive web app (PWA) for coordinating pickup basketball games. It provides real-time voting, scheduled notifications, and daily game-readiness summaries, all deployable via Docker with a modern frontend and backend stack.

---

## Features

- **PWA Frontend**: Installable on desktop and mobile (Windows, Mac, Android, iOS) with offline support and push notifications.
- **Real-Time Voting**: Vote "Yes", "No", "Maybe", "Yes (if enough for 3's)", or "Yes (if enough for 5's)". See live counts and readiness for 3v3 and 5v5 games.
- **Conditional Voting**: "Yes (if 3's)" and "Yes (if 5's)" only count toward readiness if enough players are available (6 for 3v3, 10 for 5v5).
- **Scheduled Announcements**: Configurable cron-based messages (e.g., "Game today @ 4:30?") are broadcast to all users at set times.
- **Daily Summary**: At a configured time each day, the app sends a summary message:
  - If no "yes" votes: no message.
  - If at least one "yes" but not enough for a game: "looks like no game today".
  - If enough for a game: "looks like game on for XvX" (X = half the weighted total, see below).
- **Weighted Totals**: Summary logic uses strict yes votes, half the maybes, and conditional yeses (if thresholds met) to compute readiness.
- **Browser Notifications**: Users are prompted to enable notifications for vote updates and scheduled messages.
- **Dockerized Deployment**: Multi-stage Dockerfile builds frontend and backend, runs with uWSGI and nginx. Docker Compose included.
- **Poetry for Backend**: Python dependencies managed with Poetry for reproducible builds.
- **Configurable via .env**: All secrets and schedule settings are loaded from environment variables using python-decouple.

---

## Tech Stack

**Frontend:**
- Vue 3 (Vite)
- socket.io-client
- Service Worker & manifest.json for PWA

**Backend:**
- Flask + Flask-SocketIO
- APScheduler (for cron and daily jobs)
- python-decouple (env config)
- Poetry (dependency management)

**Hosting:**
- gevent (serves Flask app)
- Docker & Docker Compose
(Reverse proxy or web server in front of this is left to the user)

---

## How It Works

1. **Voting:**
	- Open the app and vote your availability.
	- Options: Yes, Yes (if 3's), Yes (if 5's), Maybe, No.
	- Votes update in real time for all users.
	- Readiness for 3v3 (6+) and 5v5 (10+) is shown.

2. **Scheduled Messages:**
	- At configured times (e.g., 7 AM Tue/Thu), a message like "Game today @ 4:30?" is broadcast to all users.

3. **Game Status:**
	- As votes are sent, a "weighted total" is calculated
	  - Weighted total = Yes votes + floor(Maybe/2) + Yes-if-3 (if Yes+Yes-if-3 ≥ 6) + Yes-if-5 (if Yes+Yes-if-5 ≥ 10)
	- If weighted total ≥ 6: "looks like game on for XvX" (X = floor(weighted total/2))
	- If at least one yes but total < 4: "looks like no game today"
	- If no yes votes: no message sent

4. **Notifications:**
	- Users are prompted to enable browser notifications for vote updates and scheduled/summarized messages.

5. **PWA:**
	- App can be installed to home screen/desktop.

---

## Configuration

All settings are managed via environment variables. See `app/backend/.env.example` and `hosting/.env.example` for documentation.

Key variables:

- `SECRET_KEY`: Flask secret key
- `SCHEDULE_CRON`: Cron for scheduled message (e.g., `0 7 * * 2,4`)
- `SCHEDULE_MESSAGE`: Message to broadcast (e.g., `Game today @4:30?`)
- `TZ`: Timezone for scheduling and logging

---

## Development & Deployment

### Local Development

1. Copy `.env.example` to `.env` in `app/backend/` and fill in values.
2. Install backend dependencies with Poetry:
	```sh
	cd app/backend
	poetry install
	```
3. Install frontend dependencies and compile:
	```sh
	cd app/frontend
	npm install
	npm run build
	```
4. Run backend:
	```sh
	poetry run python app.py
	```

### Docker Compose

1. Build and run:
	```sh
	docker compose -f hosting/docker-compose.yml up --build
	```
2. The app will be available at http://localhost:4080

  (the "40" is the default for "PORT_PREFIX")
---

## File Structure

- `app/frontend/` — Vue 3 frontend (Vite, PWA)
- `app/backend/` — Flask backend (SocketIO, APScheduler)
- `hosting/` — Dockerfile, nginx, uWSGI, compose config

---

## License

MIT
