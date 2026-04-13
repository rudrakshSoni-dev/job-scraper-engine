# 🚀 Job Scraper Engine (Batch-Based)

A **production-oriented job aggregation system** that uses **offline scraping + fast API delivery**.

> No real-time scraping. No user latency. Designed for reliability and low cost.

---

**Get Access here:** https://job-scraper-spuce.vercel.app

## 🧠 Architecture

```
Scheduler → Scraper → PostgreSQL → FastAPI → Client
```

* **Scraping** runs periodically (not user-triggered)
* **Data stored** in PostgreSQL
* **API is read-only** → instant responses
* **Dockerized** for easy deployment

---

## ⚙️ Tech Stack

* **Backend**: FastAPI
* **Scraping**: Playwright
* **Database**: PostgreSQL (SQLAlchemy)
* **Queue/Scheduler**: Celery + Redis *(optional)*
* **Containerization**: Docker + Docker Compose

---

## 🎯 Why this design?

Traditional approach:

```
User request → scrape → wait 30–60s → return data ❌
```

This system:

```
Background scraping → store → instant API response ✅
```

### Benefits:

* ⚡ Instant API (<100ms)
* 💸 No proxy dependency (or minimal)
* 🔒 Reduced blocking risk
* 📈 Scales easily

---

## 📦 Features

* Batch scraping pipeline
* Persistent job storage
* Fast search API
* Docker-based deployment
* Ready for multi-source scraping
* Low-cost VPS compatible (2GB RAM)

---

## 🏗️ Project Structure

```
app/
 ├── api/           # FastAPI routes
 ├── scraper/       # Playwright scrapers
 ├── tasks/         # Scheduler / background jobs
 ├── db/            # Models & DB config
 └── main.py        # App entrypoint
```

---

## 🚀 Getting Started

### 1. Clone repo

```
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

### 2. Setup environment

Create `.env`:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=jobs_db

DATABASE_URL=postgresql://postgres:postgres@postgres:5432/jobs_db
REDIS_URL=redis://redis:6379/0
```

---

### 3. Run with Docker

```
docker compose up -d --build
```

---

### 4. Verify

```
docker ps
curl http://localhost:8000/health
```

---

## 📡 API Endpoints

### Health Check

```
GET /health
```

---

### Get Jobs

```
GET /jobs?query=backend
```

Response:

```json
[
  {
    "title": "Backend Developer",
    "company": "XYZ",
    "location": "India",
    "link": "..."
  }
]
```

---

## ⏰ Scraping Strategy

* Runs periodically (cron / Celery beat)
* Stores jobs in DB
* Avoids duplicate entries
* Can be extended to multiple sources

---

## ⚠️ Notes on Scraping

* Some sites (e.g., Indeed) use heavy bot protection
* System is designed to:

  * minimize scraping frequency
  * avoid real-time scraping
* Proxy support can be added if needed

---

## 🧪 Development

Run locally:

```
uvicorn app.main:app --reload
```

---

## 🛠️ Future Improvements

* [ ] Multi-source aggregation
* [ ] Deduplication logic (unique jobs)
* [ ] Ranking / scoring system
* [ ] Proxy fallback system
* [ ] Caching layer (Redis)
* [ ] Frontend dashboard

---

## 💡 Design Philosophy

> “Scrape less. Store more. Serve instantly.”

---

## 📄 License

MIT
