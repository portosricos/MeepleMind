# 🎲 MeepleMind - Premium Board Game Suggestion System

**MeepleMind** is a decoupled full-stack board game recommendation platform powered by a **FastAPI REST API Backend**, a **Streamlit Frontend Client**, linear algebra (Cosine Similarity), local AI (Ollama Phi-3), **Docker Containerization**, and **Locust Performance Load Testing**. Built on a dataset of over 22,000 board games mined from BoardGameGeek (BGG), it allows users to discover new board games based on feature similarity, exact physical constraints, and live BGG user profile imports.

---

## 🏗️ Architecture Overview

MeepleMind decouples presentation from computation and includes a dedicated performance stress-testing harness:

```text
                                  docker-compose.yml
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                  │
 │   ┌───────────────────────────┐   HTTP REST API   ┌───────────────────────────┐  │
 │   │  Frontend Container       │ ────────────────> │  Backend Container        │  │
 │   │  (Streamlit)              │  http://backend:8000  (FastAPI)               │  │
 │   │  Port 8502 (Host: 8502)   │ <──────────────── │  Port 8000 (Host: 8000)   │  │
 │   └───────────────────────────┘   JSON Responses  └───────────────────────────┘  │
 │                                                         ▲                        │
 │   ┌───────────────────────────┐                         │ HTTP Load Tests        │
 │   │  Locust Stress Tester     │ ────────────────────────┘                        │
 │   │  (Port 8089 - Web UI)     │                                                  │
 │   └───────────────────────────┘                                                  │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Locust Performance & Load Testing

We use **Locust** to benchmark sub-millisecond vector similarity calculations and API throughput under concurrent load.

### Option A: Running Locust via Docker Compose (Recommended)
Launch the entire stack including the Locust web dashboard:
```powershell
docker compose up --build -d
```
- Open **`http://localhost:8089`** in your browser.
- Set Host to `http://backend:8000`, enter your desired number of concurrent users (e.g. 50 users, spawn rate 5/sec), and click **Start swarming**.

### Option B: Running Locust Locally
If running the app without Docker:
```powershell
# 1. Start the FastAPI backend (Terminal 1)
python scripts/run_backend.py

# 2. Launch Locust UI (Terminal 2)
locust -f scripts/locustfile.py --host http://localhost:8000
```
- Open **`http://localhost:8089`** to monitor real-time Requests Per Second (RPS), response latency percentiles (50th, 95th, 99th), and zero-error rates.

---

## 🐳 Running with Docker

```powershell
# Build and launch all 4 containers (backend, frontend, ollama, locust)
docker compose up --build -d
```

- **Frontend Dashboard:** `http://localhost:8502`
- **Backend API & Swagger Docs:** `http://localhost:8000/docs`
- **Locust Load Generator:** `http://localhost:8089`

To stop the containers:
```powershell
docker compose down
```

---

## 🚀 Running Locally (Without Docker)

```powershell
# 1. Activate virtual environment & install requirements
python -m venv venv
.\venv\Scripts\activate
pip install -r requirement.txt

# 2. Launch services in separate terminals:
# Terminal 1 (Backend API):
python scripts/run_backend.py

# Terminal 2 (Streamlit UI):
streamlit run app_boardgame.py
```

---

## 🔑 BGG API Access Token (Optional)

BoardGameGeek updated its API security in October 2025. Create a `.env` file in the root directory:
```env
BGG_API_TOKEN=your_registered_bgg_bearer_token_here
```

---

## 📁 Project Structure

```text
├── docker-compose.yml       # Docker Compose multi-container orchestrator (4 services)
├── Dockerfile.backend       # Docker image definition for FastAPI Backend & Locust
├── Dockerfile.frontend      # Docker image definition for Streamlit Frontend UI
├── .dockerignore            # Excludes virtual environments and build cache
├── app_boardgame.py         # Main Streamlit frontend client entrypoint
├── recommender.py           # Import compatibility shim -> src.recommender
├── train_recommender.py     # Script launcher shim -> scripts.train_recommender
├── check_bgg.py             # Script launcher shim -> scripts.check_bgg
├── src/                     # Core application source package
│   ├── api/                 # FastAPI REST API Backend
│   │   ├── main.py          # FastAPI app & CORS middleware
│   │   ├── routes.py        # REST API endpoints (/recommend, /metadata, /bgg-collection, /explain)
│   │   └── schemas.py       # Pydantic request & response models
│   ├── recommender/         # Recommendation engine & BGG XML API client
│   │   ├── engine.py        # Vector similarity matching & filters
│   │   └── bgg_api.py       # Live BoardGameGeek XML API parser
│   ├── ui/                  # Streamlit User Interface
│   │   ├── api_client.py    # HTTP client connecting to http://localhost:8000
│   │   ├── styles.py        # Custom CSS styling tokens
│   │   ├── components.py    # Card & badge UI renderers
│   │   └── views.py         # Dashboard layout & controls
│   └── utils/               # Utilities & configuration
│       ├── ai_explainer.py  # Local Ollama / Phi-3 API client
│       └── config.py        # Project path & environment settings
├── scripts/                 # Execution & data processing scripts
│   ├── locustfile.py        # Locust load testing tasks & user scenarios
│   ├── run_backend.py       # FastAPI Uvicorn server launcher (port 8000)
│   ├── train_recommender.py # Dataset merger & pickle matrix exporter
│   └── check_bgg.py         # BGG API connectivity diagnostics
├── legacy/                  # Archived prototype drafts
├── notebooks/               # Data exploration Jupyter notebooks
├── docs/                    # Presentations, guides, and UI screenshots
├── raw_data/                # Raw BGG CSV datasets
├── processed_games.pkl      # Precalculated feature matrix & metadata
├── requirement.txt          # Python dependencies
├── .env                     # Local environment secrets (BGG Token)
└── .gitignore               # Git ignored files & directories
```

---

## 📄 License
This project is created for educational and academic data mining presentation purposes.
