[[_TOC_]]

# 🏀 Hoop It Up Documentation: Overview

Welcome to the **Hoop It Up** documentation hub.

`Hoop It Up` is a self-hosted, Progressive Web App (PWA) designed to eliminate the logistical headache of organizing pickup basketball games. By combining real-time communication, smart conditional voting logic, and automated push notifications, it helps squads quickly answer the age-old question: *"Do we have enough for a game today?"*

---

## Core Value Proposition

Unlike generic polling tools, Hoop It Up is purpose-built for sports coordination:

* **Dynamic Readiness Logic:** It doesn't just count heads; it calculates weighted availability (handling "maybes" and conditional numbers) to determine if you have enough for a clean 3v3 or 5v5 matchup.
* **No-App-Store PWA:** Users can install the application directly from their mobile or desktop browser, gaining access to native-like push notifications without navigating app stores.
* **Fully Self-Hosted & Dockerized:** Complete ownership of your data and scheduling intervals with a lightweight footprint.

---

## 🛠️ The Tech Stack

Hoop It Up is split into a modern decoupled architecture, containerized for easy deployment:

| Layer | Technology | Purpose |
| --- | --- | --- |
| **Frontend** | Vue 3 (Vite) | Fast, reactive user interface optimized for courtside mobile use. |
| **Real-time** | Socket.io / Flask-SocketIO | Drives instant, multi-client vote updates without page refreshes. |
| **Backend** | Flask (Python) | Lightweight REST API and application logic handler. |
| **Scheduler** | APScheduler | Manages automated cron-based game alerts and daily summaries. |
| **Environment** | Poetry & Python-Decouple | Strict, predictable dependency management and runtime configurations. |
| **Deployment** | Docker & Docker Compose | Multi-stage production builds utilizing `gevent` for concurrent connection handling. |

---

## How the Game Logic Works

The core engine of Hoop It Up revolves around an automated **Game Readiness Lifecycle** driven by user votes and server-side crons:

```
[Users Vote] ──> [Socket.io Broadcasts Live Counts] ──> [Cron Trigger] ──> [Weighted Total Evaluated] ──> [Push Notification Sent]

```

### 1. Dynamic Voting Options

Users aren't limited to a binary "Yes" or "No". They can vote:

* `Yes` / `No` / `Maybe`
* `Yes (if enough for 3's)` — Threshold triggers at $\ge 6$ total players.
* `Yes (if enough for 5's)` — Threshold triggers at $\ge 10$ total players.

### 2. The Weighted Total Formula

The backend evaluates daily readiness using a strict formula at a designated summary time:

$$\text{Weighted Total} = \text{Strict Yes} + \lfloor\frac{\text{Maybe}}{2}\rfloor + \text{Conditional 3s (if threshold met)} + \text{Conditional 5s (if threshold met)}$$

### 3. Automated Summaries

Based on the formula result, the app automates communication:

* **Game On:** If the total hits a threshold, a broadcast fires: *"Looks like game on for XvX"* (where $X = \lfloor\text{Weighted Total} / 2\rfloor$).
* **Missed Threshold:** If there is interest but numbers fall short: *"Looks like no game today"*.
* **Inactivity:** If no "Yes" votes are logged, the app remains silent.

---

## Repository Architecture

When exploring the codebase, here is where everything lives:

* `app/frontend/` — Vue 3 source code, service workers for offline/PWA capabilities, and asset manifests.
* `app/backend/` — Flask application, socket mappings, scheduler tasks, and Poetry configurations.
* `hosting/` — Production-ready deployment configuration including Dockerfiles and docker-compose stack config

---

## Deploying

Ready to get Hoop It Up running for your local league or pickup crew? Proceed to the next steps:

* Clone the repo 
  
  `git clone https://github.com/mshafer1/hoopitup.git`
  
* Copy example env file to make your own copy

  `cp hosting/env.example hosting/.env`

* Edit `hosting/.env` to suit your group / needs

  (Configure time zone, what message to send, when, etc.)

* `cd hosting`

* `docker compose up -d`

  App will be live at http://localhost:4080 (the 40 part can be changed by setting `port_prefix` in the .env file)

⚠️ Warning ⚠️: The reader is left to determine a reverse proxy to use.
