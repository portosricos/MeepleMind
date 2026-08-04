# 🎲 MeepleMind - Premium Board Game Suggestion System

**MeepleMind** is an enterprise-grade, decoupled full-stack board game recommendation platform. Powered by a **FastAPI REST API Backend**, a **Streamlit Frontend Client**, linear algebra (Cosine Similarity), local AI (Ollama Phi-3), **Docker Containerization**, and **Locust Performance Load Testing**, it allows users to discover new board games from a dataset of over 22,000 games mined from BoardGameGeek (BGG).

---

## 🏗️ Architecture Overview

MeepleMind decouples presentation from computation and includes a complete containerized suite and performance stress-testing harness:

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
 │                                                                                  │
 │   ┌───────────────────────────┐                                                  │
 │   │  Ollama Local AI Engine   │                                                  │
 │   │  (Port 11434 - LLM)       │                                                  │
 │   └───────────────────────────┘                                                  │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Master Testing Guide (How to Test Everything)

Choose either **Method A (Docker - Recommended)** or **Method B (Local Python Environment)** to test the entire system.

---

### 🐳 Method A: Testing Everything with Docker Compose (Recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.

#### 1. Build & Launch All 4 Containers
In your terminal, run:
```powershell
docker compose up --build -d
```

This will automatically launch:
* **FastAPI Backend Server** on `http://localhost:8000`
* **Streamlit Frontend UI** on `http://localhost:8502`
* **Locust Load Tester** on `http://localhost:8089`
* **Ollama AI Engine** on `http://localhost:11434`

#### 2. Test Streamlit Frontend Application (`http://localhost:8502`)
* Open your browser and navigate to **`http://localhost:8502`**.
* Verify that the green architecture badge appears:
  `🟢 System Architecture: Decoupled Mode — Streamlit Frontend connected to FastAPI Backend REST API (http://localhost:8000)`
* **Test Manual Search:** Select liked games like *Catan* or *Pandemic* and verify the top calculated recommendations update instantly.
* **Test Range Filters:** Adjust the player count slider, playtime duration selector, and complexity range slider.
* **Test BGG Sync:** Go to the *Import from BoardGameGeek Collection* tab, enter username `portos`, and click **Sync BGG Collection**.
* **Test AI Explainer:** Click **🔮 Ask AI why I will love this** on any recommendation card.

#### 3. Test FastAPI REST API & Interactive Docs (`http://localhost:8000/docs`)
* Open **`http://localhost:8000/docs`** to access the interactive Swagger UI.
* Try executing `GET /health` to verify `{"status": "ok"}`.
* Try executing `GET /api/v1/metadata` to see the total catalog count (21,925 games) and lists of mechanics/themes.
* Try executing `POST /api/v1/recommend` with custom JSON payloads.

#### 4. Test Locust Performance Load Generator (`http://localhost:8089`)
* Open **`http://localhost:8089`** in your browser.
* Ensure **Host** is set to `http://backend:8000`.
* Set **Number of users** to `50` and **Spawn rate** to `5`.
* Click **Start swarming** to watch real-time Requests Per Second (RPS), average latency (ms), and zero-error performance charts.

#### 5. Pull Model into Containerized Ollama (One-time AI Setup)
To enable local AI gameplay explanations inside the Docker container:
```powershell
docker exec -it meeplemind-ollama ollama pull phi3
```

#### 6. Stop Containers
When finished testing:
```powershell
docker compose down
```

---

### 💻 Method B: Testing Everything Locally (Terminal by Terminal)

If you prefer testing directly on your local machine without Docker:

#### 1. Setup Virtual Environment & Install Dependencies
```powershell
# Navigate to project directory
cd data_mining_final_project

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\activate

# Install all requirements
pip install -r requirement.txt
```

#### 2. Start Local AI Server (Ollama)
Ensure [Ollama](https://ollama.com) is installed and running on your computer:
```powershell
# Open terminal and pull the phi3 model
ollama pull phi3
```

#### 3. Launch FastAPI Backend REST API (Terminal 1)
```powershell
.\venv\Scripts\activate
python scripts/run_backend.py
```
* **Verify:** Open **`http://localhost:8000/docs`** to see the Swagger documentation.

#### 4. Launch Streamlit Frontend Client (Terminal 2)
In a second terminal window:
```powershell
.\venv\Scripts\activate
streamlit run app_boardgame.py
```
* **Verify:** Open **`http://localhost:8502`** to interact with the web dashboard.

#### 5. Launch Locust Load Testing Benchmark (Terminal 3)
In a third terminal window:
```powershell
.\venv\Scripts\activate
locust -f scripts/locustfile.py --host http://localhost:8000
```
* **Verify:** Open **`http://localhost:8089`** to run load tests against the local backend server.

---

## 🎯 Key Application Features & Verification Checklist

| Feature | How to Verify | Expected Outcome |
| :--- | :--- | :--- |
| **Cosine Vector Matching** | Select *Catan* or *Pandemic* | Recommends games with matching mechanics & themes (80% similarity + 20% BGG rating score). |
| **BGG Collection Sync** | Input BGG Username `portos` | Pulls owned games live via BGG XML API2 and matches against local 22k catalog. |
| **Exclude Owned Games** | Check *🚫 Exclude Owned Games* | Excludes user's owned games from candidate recommendations. |
| **Profile-Wide KNN Matching** | Select *Entire synced collection* | Runs Top-5 K-Nearest Neighbors (KNN) pairwise matching across user's entire library. |
| **Physical Range Filters** | Adjust sliders for Players / Playtime / Weight | Strict mathematical candidate masking excludes games outside physical constraints. |
| **Local LLM Explainer** | Click *🔮 Ask AI why I will love this* | Local Ollama `phi3` generates custom 3-sentence gameplay explanation. |
| **Load Benchmark Tests** | Run Locust swarm at `http://localhost:8089` | Monitors RPS, latency percentiles, and zero failure rates under traffic. |

---

## 🔑 BGG API Access Token (Optional)

BoardGameGeek updated its API security policy in October 2025. If you wish to use live BGG Collection Sync, create a `.env` file in the root directory:
```env
BGG_API_TOKEN=your_registered_bgg_bearer_token_here
```
*(Note: `.env` is listed in `.gitignore` so your personal credentials are never committed to GitHub.)*

---

## 📁 Clean Project Structure

```text
├── docker-compose.yml       # Multi-container Docker orchestrator (4 services)
├── Dockerfile.backend       # Docker build context for FastAPI REST API Backend
├── Dockerfile.frontend      # Docker build context for Streamlit Frontend UI
├── .dockerignore            # Excludes build cache and virtual environments
├── app_boardgame.py         # Main Streamlit frontend client entrypoint
├── recommender.py           # Import compatibility shim -> src.recommender
├── train_recommender.py     # Script launcher shim -> scripts.train_recommender
├── check_bgg.py             # Script launcher shim -> scripts.check_bgg
├── src/                     # Core application source package
│   ├── api/                 # FastAPI REST API Backend service
│   │   ├── main.py          # FastAPI app & CORS middleware
│   │   ├── routes.py        # REST API endpoints (/recommend, /metadata, /bgg-collection, /explain)
│   │   └── schemas.py       # Pydantic request & response models
│   ├── recommender/         # Recommendation engine & BGG XML API client
│   │   ├── engine.py        # Vector similarity matching & range filters
│   │   └── bgg_api.py       # Live BoardGameGeek XML API parser
│   ├── ui/                  # Streamlit User Interface
│   │   ├── api_client.py    # HTTP client connecting to http://localhost:8000
│   │   ├── styles.py        # Custom CSS styling tokens
│   │   ├── components.py    # Card & badge UI renderers
│   │   └── views.py         # Dashboard layout & controls
│   └── utils/               # Infrastructure helpers
│       ├── ai_explainer.py  # Local Ollama / Phi-3 API client with host fallback
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
