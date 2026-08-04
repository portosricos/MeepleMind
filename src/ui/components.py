import streamlit as st
from src.utils.ai_explainer import generate_game_explanation

def render_hero_header():
    """Render Hero title banner."""
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">🎲 MeepleMind</div>
        <div class="hero-subtitle" style="font-size: 1.2rem; color: #94a3b8; font-weight: 500;">
            Board Game Suggestion System Powered by Data Mining & Local AI
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_game_card(rec: dict, liked_games: list):
    """Render a single board game recommendation card."""
    st.markdown('<div class="game-card">', unsafe_allow_html=True)
    
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
        if len(liked_games) > 0:
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
        if len(liked_games) > 0:
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
                explanation = generate_game_explanation(rec, liked_games, model="phi3")
                st.markdown(f"<div style='font-size: 0.9rem; color: #e2e8f0; line-height: 1.5; margin-top: 0.5rem; background: rgba(255,255,255,0.02); padding: 0.75rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04);'>{explanation}</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
