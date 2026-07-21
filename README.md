# 🎲 MeepleMind - Premium Board Game Suggestion System

**MeepleMind** is a data-driven board game recommendation dashboard powered by linear algebra (Cosine Similarity) and local AI (Ollama Phi-3). Built on a dataset of over 22,000 board games mined from BoardGameGeek (BGG), it allows users to discover new board games based on feature similarity, exact physical constraints, and live BGG user profile imports.

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

## 🏗️ Architecture Overview

MeepleMind uses a **deterministic content-based calculation engine** rather than a black-box machine learning model or pure text vector search:

1. **Feature Vectors (382 Dimensions):** Every game is represented as a binary vector across 382 unique categories, mechanics, and themes.
2. **Cosine Similarity:** Computes the mathematical angle between user preference vectors and candidate game vectors:
   $$\text{Similarity}(A, B) = \frac{A \cdot B}{\|A\| \|B\|}$$
3. **Hybrid Score:** Blends feature similarity with BGG community ratings:
   $$\text{Final Score} = (\text{Cosine Similarity} \times 0.8) + (\text{Normalized Bayes Rating} \times 0.2)$$
4. **Fact-Grounded LLM Explainer:** The local LLM (Phi-3) receives the computed shared features directly in the prompt, eliminating hallucinations.

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

# Install required dependencies
pip install -r requirement.txt
```

### 3. Local AI Setup (Ollama)
Ensure the Ollama application is running, then pull the `phi3` model:
```bash
ollama pull phi3
```

---

## 🚀 How to Run the Application

1. Make sure your virtual environment is active.
2. Launch the Streamlit server:
   ```bash
   streamlit run app_boardgame.py
   ```
3. Open your browser and navigate to the address shown in your terminal (default: `http://localhost:8501` or `http://localhost:8502`).

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
├── app_boardgame.py         # Streamlit web application & UI layout
├── recommender.py           # Cosine similarity engine & candidate filter logic
├── train_recommender.py     # Data preprocessing & feature matrix generator
├── processed_games.pkl      # Precalculated feature matrix & metadata pickle
├── requirement.txt          # Python dependencies
├── .env                     # Local environment variables (BGG Token)
└── .gitignore               # Ignored files (venv, raw data, secrets)
```

---

## 📄 License
This project is created for educational and academic data mining presentation purposes.
