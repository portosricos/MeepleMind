# 🎲 MeepleMind - Premium Board Game Suggestion System

**MeepleMind** is a decoupled full-stack board game recommendation platform powered by a **FastAPI REST API Backend**, a **Streamlit Frontend Client**, linear algebra (Cosine Similarity), local AI (Ollama Phi-3), and **Docker Containerization**. Built on a dataset of over 22,000 board games mined from BoardGameGeek (BGG), it allows users to discover new board games based on feature similarity, exact physical constraints, and live BGG user profile imports.

---

## 🏗️ Architecture Overview

MeepleMind decouples presentation from computation and can be run either locally or via Docker Compose:

```text
                                  docker-compose.yml
 ┌──────────────────────────────────────────────────────────────────────────────────┐
 │                                                                                  │
 │   ┌───────────────────────────┐   HTTP REST API   ┌───────────────────────────┐  │
 │   │  Frontend Container       │ ────────────────> │  Backend Container        │  │
 │   │  (Streamlit)              │  http://backend:8000  (FastAPI)               │  │
 │   │  Port 8502 (Host: 8502)   │ <──────────────── │  Port 8000 (Host: 8000)   │  │
 │   └───────────────────────────┘   JSON Responses  └───────────────────────────┘  │
 │                                                                                  │
 └──────────────────────────────────────────────────────────────────────────────────┘
```

### 🛰️ REST API Endpoints (`http://localhost:8000`):
- **`GET /health`**: Health status check.
- **`GET /api/v1/metadata`**: Serves catalog metrics, game titles list, categories, mechanics, and themes.
- **`POST /api/v1/recommend`**: Accepts user criteria, filters, and liked games JSON payload, executing vector dot-product similarity calculations.
- **`POST /api/v1/bgg-collection`**: Fetches user collections live via BoardGameGeek XML API2.
- **`POST /api/v1/explain`**: Calls local Ollama `phi3` model for AI explanations.
- **`Swagger Interactive Documentation`**: Accessible at `http://localhost:8000/docs`.

---

## 🐳 Running with Docker (Recommended)

Run the entire application (Backend API + Frontend UI) with a single command:

```powershell
# Build and launch containers in detached mode
docker compose up --build -d
```

- **Frontend Dashboard:** Open `http://localhost:8502`
- **Backend API & Docs:** Open `http://localhost:8000/docs`

To stop the containers:
```powershell
docker compose down
```

---

## 🚀 Running Locally (Without Docker)

### 1. Environment Setup
```powershell
# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirement.txt
```

### 2. Launch Services
In two separate terminals:

```powershell
# Terminal 1: FastAPI Backend REST API
python scripts/run_backend.py

# Terminal 2: Streamlit Frontend Client
streamlit run app_boardgame.py
```

---

## 🔑 BGG API Access Token (Optional)

BoardGameGeek updated its API security in October 2025. If you wish to use the live BGG Collection Sync, create a `.env` file in the root directory:
```env
BGG_API_TOKEN=your_registered_bgg_bearer_token_here
```
*(Note: `.env` is listed in `.gitignore` to keep your credentials secure.)*

---

## 📁 Project Structure

```text
├── docker-compose.yml       # Docker Compose multi-container orchestrator
├── Dockerfile.backend       # Docker image definition for FastAPI Backend API
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
