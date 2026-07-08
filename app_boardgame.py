import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import xml.etree.ElementTree as ET
import time
from recommender import load_data, recommend_games

# Set page config
st.set_page_config(
    page_title="MeepleMind - Board Game Recommender",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    .stApp {
        background-color: #0b0f19;
        background-image: radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                          radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.08) 0px, transparent 50%);
        color: #f8fafc;
        font-family: 'Outfit', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .hero-container {
        padding: 2rem;
        background: rgba(30, 41, 59, 0.35);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 50px rgba(0, 0, 0, 0.3);
    }
    .hero-title {
        background: linear-gradient(135deg, #a5b4fc, #6366f1, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .game-card {
        background: rgba(17, 24, 39, 0.65) !important;
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.25);
    }
    .game-card:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2);
    }
    
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.75rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-similarity {
        background: rgba(99, 102, 241, 0.15);
        color: #818cf8;
        border: 1px solid rgba(99, 102, 241, 0.35);
    }
    .badge-rating {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.35);
    }
    .badge-weight {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.35);
    }
    .badge-generic {
        background: rgba(255, 255, 255, 0.05);
        color: #e2e8f0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .badge-shared {
        background: rgba(6, 182, 212, 0.15);
        color: #22d3ee;
        border: 1px solid rgba(6, 182, 212, 0.35);
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
    }
    .stat-val {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
    }
    
    /* Input background styling */
    div[data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to query local Ollama model
def ask_ollama(prompt, model="phi3"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        response.raise_for_status()
        return response.json()["response"].strip()
    except Exception as e:
        return f"Error communicating with local AI model: {str(e)}. Please make sure Ollama is running and has the '{model}' model pulled."

# Load preprocessed dataset
try:
    data = load_data()
    df = data['metadata']
    categories = data['categories']
    mechanics = sorted(data['mechanics'])
    themes = sorted(data['themes'])
    all_names = sorted(df['Name'].tolist())
except Exception as e:
    st.error(f"Failed to load dataset: {e}. Make sure train_recommender.py has been run.")
    st.stop()

# Header / Hero
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎲 MeepleMind</div>
    <div class="hero-subtitle" style="font-size: 1.2rem; color: #94a3b8; font-weight: 500;">
        Board Game Suggestion System Powered by Data Mining & Local AI
    </div>
</div>
""", unsafe_allow_html=True)

# Layout Setup: Sidebar Filters
with st.sidebar:
    st.markdown("### 🔍 Filters & Criteria")
    st.caption("Customize ranges to filter candidates.")
    st.markdown("---")
    
    # 1. Player Count Range
    player_count_range = st.slider(
        "👥 Player Count Range",
        min_value=1,
        max_value=12,
        value=(2, 4),
        help="Filter games that support at least some range matching these player counts."
    )
    
    # 2. Playtime Preset Ranges
    playtime_option = st.selectbox(
        "⏳ Playtime Duration",
        options=[
            "Any Duration",
            "Short (< 30 min)",
            "Medium (30 - 60 min)",
            "Long (60 - 120 min)",
            "Epic (120 - 200 min)",
            "Legendary (200+ min)"
        ],
        index=0,
        help="Select games based on their average max playtime range."
    )
    
    # 3. Complexity Range Slider (1.0 to 5.0)
    complexity_range = st.slider(
        "🧠 Complexity Range (Weight)",
        min_value=1.0,
        max_value=5.0,
        value=(1.0, 5.0),
        step=0.1,
        help="1.0 = Very Simple, 5.0 = Very Complex. Filter games by their complexity rating."
    )
    
    # Show active complexity labels based on the slider selection
    min_w, max_w = complexity_range
    active_labels = []
    if min_w < 1.8:
        active_labels.append("Light/Easy")
    if (min_w <= 2.5 and max_w >= 1.8):
        active_labels.append("Medium-Easy")
    if (min_w <= 3.5 and max_w >= 2.5):
        active_labels.append("Medium-Heavy")
    if max_w > 3.5:
        active_labels.append("Heavy/Complex")
    
    st.caption(f"Active Sub-complexities: **{', '.join(active_labels)}**")
    st.markdown("---")
    
    # 4. Categories Multi-select
    selected_cats = st.multiselect(
        "📂 Categories",
        options=categories,
        help="Filter on games matching at least one category."
    )
    
    # 5. Mechanics Multi-select
    selected_mechs = st.multiselect(
        "⚙️ Mechanics",
        options=mechanics,
        help="Filter on games featuring at least one mechanic."
    )
    
    # 6. Themes Multi-select
    selected_themes = st.multiselect(
        "🪐 Themes",
        options=themes,
        help="Filter on games matching at least one theme."
    )
    
    st.markdown("---")
    if st.button("Reset Filters", use_container_width=True):
        st.session_state.liked_games = []
        st.rerun()

# Main Body: Game Selection
st.markdown("### 1. Select Board Games You Enjoy")
st.caption("Tell us what games you love, and we will find others with similar mechanics and themes.")

if 'liked_games' not in st.session_state:
    st.session_state.liked_games = []

# Tabs for Game Input selection
tab_select, tab_bgg_import = st.tabs(["🔍 Search & Add Manually", "📥 Import from BoardGameGeek Collection"])

with tab_select:
    liked_input = st.multiselect(
        "Type to search and add games to your liked list:",
        options=all_names,
        default=st.session_state.liked_games,
        key="manual_games_input"
    )
    st.session_state.liked_games = liked_input
    
    # Quick reset button for manual list
    if st.session_state.liked_games:
        if st.button("🗑️ Clear My List", key="clear_manual"):
            st.session_state.liked_games = []
            st.rerun()

with tab_bgg_import:
    st.markdown("##### Sync with your BoardGameGeek Account")
    st.markdown(
        "⚠️ *Note: BoardGameGeek updated its API policies in October 2025. "
        "A registered developer Bearer Token is now required to query user collections.* "
        "You can register and obtain a token from [BGG's XML API Documentation Page](https://boardgamegeek.com/using_the_xml_api)."
    )
    
    col1, col2 = st.columns([1, 1])
    with col1:
        bgg_username = st.text_input("BGG Username", placeholder="e.g. portos", key="bgg_username_input")
    with col2:
        bgg_token = st.text_input("BGG API Access Token (Bearer Token)", type="password", placeholder="Paste your token here...", key="bgg_token_input")
        
    fetch_btn = st.button("🔄 Sync BGG Collection", use_container_width=True)
        
    if fetch_btn and bgg_username.strip():
        if not bgg_token.strip():
            st.error("BGG API requires an Access Token. Please paste your BGG Bearer Token above.")
        else:
            with st.spinner("Connecting to BGG XML API..."):
                url = f"https://boardgamegeek.com/xmlapi2/collection?username={bgg_username.strip()}&own=1"
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Authorization': f'Bearer {bgg_token.strip()}'
                }
                success = False
                error_msg = ""
                owned_games = []
                
                # BGG API can return HTTP 202 if preparing data. We retry up to 4 times with short delays.
                for attempt in range(4):
                    try:
                        res = requests.get(url, headers=headers, timeout=15)
                        if res.status_code == 200:
                            root = ET.fromstring(res.content)
                            # Check for API error response
                            error_elem = root.find('error')
                            if error_elem is not None:
                                error_msg = error_elem.find('message').text
                                break
                            
                            items = root.findall('item')
                            for item in items:
                                name_elem = item.find('name')
                                if name_elem is not None:
                                    owned_games.append(name_elem.text)
                            success = True
                            break
                        elif res.status_code == 202:
                            time.sleep(3) # Wait for BGG to compile the list
                            continue
                        else:
                            error_msg = f"Status code {res.status_code}"
                            break
                    except Exception as e:
                        error_msg = str(e)
                        time.sleep(2)
            
            if success:
                # Match names case-insensitively with our catalog
                all_names_lower = {n.lower(): n for n in all_names}
                matched = []
                for g_name in owned_games:
                    if g_name.lower() in all_names_lower:
                        matched.append(all_names_lower[g_name.lower()])
                
                if matched:
                    st.session_state.liked_games = matched
                    st.success(f"Imported **{len(matched)}** matching games from **{bgg_username}**'s BGG collection!")
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.warning("Successfully connected, but no owned games in BGG matched our 22k game catalog.")
            else:
                st.error(f"Could not load BGG collection: {error_msg}. (Make sure your username is correct and your collection is set to public).")

# Visual Display of Current Liked Games
if st.session_state.liked_games:
    st.markdown("##### **Your Current Liked List:**")
    liked_html = " ".join(f'<span class="badge badge-similarity">🏷️ {item}</span>' for item in st.session_state.liked_games)
    st.markdown(liked_html, unsafe_allow_html=True)

st.markdown("---")

# Execute Recommendations
recs = recommend_games(
    selected_names=st.session_state.liked_games,
    player_count_range=player_count_range,
    playtime_option=playtime_option,
    complexity_range=complexity_range,
    selected_cats=selected_cats,
    selected_mechs=selected_mechs,
    selected_themes=selected_themes,
    top_n=5
)

# Display recommendations
if recs:
    st.markdown(f"### ✨ Top Recommendations ({len(recs)} games found)")
    st.caption("Ranked by combining feature similarity (80%) and board game popularity/rating (20%).")
    
    for idx, rec in enumerate(recs):
        st.markdown(f'<div class="game-card">', unsafe_allow_html=True)
        
        col_img, col_det, col_ai = st.columns([1.5, 5, 3.5])
        
        with col_img:
            if rec['ImagePath']:
                st.image(rec['ImagePath'], use_container_width=True)
            else:
                st.markdown(
                    '<div style="background:#1e293b; height:150px; border-radius:12px; display:flex; align-items:center; justify-content:center; color:#64748b;">🎲 No Cover</div>',
                    unsafe_allow_html=True
                )
                
        with col_det:
            st.markdown(f"<div style='font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;'>{rec['Name']} <span style='font-size: 0.9rem; font-weight:400; color: #64748b;'>({rec['YearPublished']})</span></div>", unsafe_allow_html=True)
            
            # Badges Row
            badge_html = ""
            if len(st.session_state.liked_games) > 0:
                badge_html += f'<span class="badge badge-similarity">🔥 {int(rec["Similarity"] * 100)}% Match</span>'
            badge_html += f'<span class="badge badge-rating">⭐ {rec["BayesAvgRating"]:.2f}/10</span>'
            
            # Determine sub-complexity labels for the specific game
            w = rec['GameWeight']
            g_lbl = "Light" if w < 1.8 else "Med-Easy" if w <= 2.5 else "Med-Heavy" if w <= 3.5 else "Heavy"
            badge_html += f'<span class="badge badge-weight">🧠 {g_lbl} ({w:.2f}/5)</span>'
            st.markdown(badge_html, unsafe_allow_html=True)
            
            # Metadata Stats
            st.markdown(f"""
            <div style='margin-bottom: 0.75rem;'>
                <span class='stat-label'>👥 Players:</span> <span class='stat-val'>{rec['MinPlayers']}-{rec['MaxPlayers']}</span>
                <span style='margin: 0 0.75rem; color: #334155;'>|</span>
                <span class='stat-label'>⏳ Playtime:</span> <span class='stat-val'>{int(rec['MinPlaytime'])}-{int(rec['MaxPlaytime'])} min</span>
                <span style='margin: 0 0.75rem; color: #334155;'>|</span>
                <span class='stat-label'>👶 Suggested Age:</span> <span class='stat-val'>{int(rec['ComAgeRec'])}+</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Categories, Mechanics, Themes lists
            cat_list = ", ".join(rec['Categories'])
            mech_list = ", ".join(rec['Mechanics'][:8]) + ("..." if len(rec['Mechanics']) > 8 else "")
            theme_list = ", ".join(rec['Themes'][:8]) + ("..." if len(rec['Themes']) > 8 else "")
            
            st.markdown(f"""
            <div style='font-size: 0.85rem; color: #cbd5e1;'>
                <strong>📂 Categories:</strong> {cat_list}<br>
                <strong>⚙️ Mechanics:</strong> {mech_list}<br>
                <strong>🪐 Themes:</strong> {theme_list}
            </div>
            """, unsafe_allow_html=True)
            
            # Shared elements badges
            if len(st.session_state.liked_games) > 0:
                shared_elements = rec['SharedCategories'] + rec['SharedMechanics'] + rec['SharedThemes']
                if shared_elements:
                    shared_html = "<div style='margin-top: 0.5rem;'><span class='stat-label' style='display:inline-block; margin-right:0.5rem;'>Shared features:</span>"
                    for element in shared_elements[:6]:
                        shared_html += f'<span class="badge badge-shared">{element}</span>'
                    if len(shared_elements) > 6:
                        shared_html += f'<span class="badge badge-generic">+{len(shared_elements)-6} more</span>'
                    shared_html += "</div>"
                    st.markdown(shared_html, unsafe_allow_html=True)
                    
        with col_ai:
            st.markdown("<div style='border-left: 1px solid rgba(255,255,255,0.08); padding-left: 1.25rem; height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<span class='stat-label'>🧠 Local AI Explainer</span>", unsafe_allow_html=True)
            
            explain_key = f"explain_{rec['BGGId']}"
            if st.button("🔮 Ask AI why I will love this", key=explain_key, use_container_width=True):
                with st.spinner("Analyzing rules, themes, and mechanics..."):
                    prompt = f"""
You are a board game expert and enthusiast. 
Explain to a user why they would love the board game: "{rec['Name']}".
The user currently loves these board games: {', '.join(st.session_state.liked_games)}.

Details for "{rec['Name']}":
- Complexity (Weight): {rec['GameWeight']}/5
- Average User Rating: {rec['AvgRating']}/10
- Play Time: {rec['MinPlaytime']}-{rec['MaxPlaytime']} minutes
- Players: {rec['MinPlayers']}-{rec['MaxPlayers']}
- Categories: {', '.join(rec['Categories'])}
- Mechanics: {', '.join(rec['Mechanics'])}
- Themes: {', '.join(rec['Themes'])}

Shared features with their liked games:
- Shared Categories: {', '.join(rec['SharedCategories'])}
- Shared Mechanics: {', '.join(rec['SharedMechanics'])}
- Shared Themes: {', '.join(rec['SharedThemes'])}

Instructions:
- Write a friendly, enthusiastic, and concise response (maximum 3 sentences).
- Explain the gameplay feel and how it leverages the shared features.
- Answer directly without starting with "Sure, here is the explanation".
"""
                    explanation = ask_ollama(prompt, model="phi3")
                    st.markdown(f"<div style='font-size: 0.9rem; color: #e2e8f0; line-height: 1.5; margin-top: 0.5rem; background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);'>{explanation}</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown(f'</div>', unsafe_allow_html=True)
else:
    st.info("No games match your selected criteria. Try adjusting your player count, playtime, or complexity filters, or select different liked games!")

# Details Accordion
st.markdown("---")
with st.expander("📚 Explore BGG Dataset Schema & Metadata"):
    st.markdown("""
    **MeepleMind** runs on processed data containing 21,925 board games mined from BoardGameGeek.
    * **Game Weight (Complexity) sub-complexities:**
        * **Light/Easy:** Weight < 1.8 (e.g. *Codenames*, *Dixit*)
        * **Medium-Easy:** Weight 1.8 - 2.5 (e.g. *Catan*, *Azul*, *Pandemic*)
        * **Medium-Heavy:** Weight 2.5 - 3.5 (e.g. *7 Wonders*, *Acquire*, *Wingspan*)
        * **Heavy/Complex:** Weight > 3.5 (e.g. *Terraforming Mars*, *Through the Ages*)
    """)
    
    st.markdown("**Dataset Sizes:**")
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Total Board Games", f"{len(df):,}")
    m_col2.metric("Total Mechanics Mapped", f"{len(mechanics)}")
    m_col3.metric("Total Themes Mapped", f"{len(themes)}")
