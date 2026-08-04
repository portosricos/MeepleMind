# 🎲 MeepleMind - Premium Board Game Suggestion System

**MeepleMind** is a decoupled full-stack board game recommendation platform powered by a **FastAPI REST API Backend**, a **Streamlit Frontend Client**, linear algebra (Cosine Similarity), and local AI (Ollama Phi-3). Built on a dataset of over 22,000 board games mined from BoardGameGeek (BGG), it allows users to discover new board games based on feature similarity, exact physical constraints, and live BGG user profile imports.

---

## 🏗️ Decoupled Architecture Overview

MeepleMind decouples presentation from computation:

```text
┌────────────────────────────────┐         HTTP REST API         ┌────────────────────────────────┐
│  Streamlit Frontend (UI)       │ ───────────────────────────>  │  FastAPI Backend Server        │
│  Port: 8502                    │  POST /api/v1/recommend       │  Port: 8000                    │
│  (src/ui/ & app_boardgame.py)  │  POST /api/v1/bgg-collection  │  (src/api/ & run_backend.py)   │
└────────────────────────────────┘ <───────────────────────────  └────────────────────────────────┘
                                           JSON Responses                      │
                                                                               ▼
                                                                  NumPy Vector Engine & Ollama
```

### 🛰️ REST API Endpoints (`http://localhost:8000`):
- **`GET /health`**: Health status check.
- **`GET /api/v1/metadata`**: Serves catalog metrics, game titles list, categories, mechanics, and themes.
- **`POST /api/v1/recommend`**: Accepts user criteria, filters, and liked games JSON payload, executing vector dot-product similarity calculations.
- **`POST /api/v1/bgg-collection`**: Fetches user collections live via BoardGameGeek XML API2.
- **`POST /api/v1/explain`**: Calls local Ollama `phi3` model for AI explanations.
- **`Swagger Interactive Documentation`**: Accessible at `http://localhost:8000/docs`.

---

## ✨ Features

- **🔍 Dual Selection Modes:**
  - **Manual Search:** Search and select games directly from our 22,000+ game catalog.
  - **Live BGG Collection Sync:** Input your BoardGameGeek username to fetch your owned collection live via the BGG XML API2.
- **🚫 Exclude Owned Games:** Filter out your existing BGG collection so suggestions only contain games you don't already own.
- **🎯 Profile-Wide Pairwise Matching:** Option to match candidate games against your entire collection using a Top-5 K-Nearest Neighbors (KNN) pairwise vector approach to prevent vector dilution.
- **🎛️ Fine-Grained Range Filters:**
  - **Player Count Range Slider:** Filter games that support your exact group size (e.g., 2 to 4 players).
  - **Playtime Presets:** Select session lengths (*Short <30m*, *Medium 30-60m*, *Long 60-120m*, *Epic 120-200m*, *Legendary 200m+*).
  - **Sub-Complexity Slider (1.0 to 5.0):** Filter games by weight (*Light*, *Medium-Easy*, *Medium-Heavy*, *Heavy*).
- **🤖 Local AI Explainer (Phi-3):** Connects to your local Ollama instance to generate custom, 3-sentence gameplay explanations based on shared mechanics and themes without hallucinations.
- **⚡ Sub-Millisecond Performance:** Feature matrix compressed to `np.int8` for sub-2ms vector dot-product calculations.

---

## 🛠️ Installation & Prerequisites

### 1. Prerequisites
- **Python 3.12+** installed on your system.
- **Ollama** installed for local AI explanations. Download from [ollama.com](https://ollama.com).

### 2. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/your-username/data_mining_final_project.git
cd data_mining_final_project

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Install required dependencies (includes fastapi & uvicorn)
pip install -r requirement.txt
```

### 3. Local AI Setup (Ollama)
Ensure the Ollama application is running, then pull the `phi3` model:
```bash
ollama pull phi3
```

---

## 🚀 How to Run the Application

In the decoupled architecture, run both the backend server and frontend client:

### Step 1: Launch the FastAPI Backend Server
```powershell
python scripts/run_backend.py
```
*The backend API will run on **`http://localhost:8000`**. You can view the OpenAPI interactive Swagger docs at **`http://localhost:8000/docs`**.*

### Step 2: Launch the Streamlit Frontend Client
In a second terminal window:
```powershell
streamlit run app_boardgame.py
```
*The Streamlit client will run on **`http://localhost:8502`** and connect automatically to the FastAPI backend REST API.*

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
