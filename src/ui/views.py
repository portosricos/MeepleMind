import streamlit as st
import time
from src.ui.styles import apply_custom_styles
from src.ui.components import render_hero_header, render_game_card
from src.ui.api_client import (
    is_backend_online,
    get_catalog_metadata,
    fetch_recommendations_api,
    sync_bgg_collection_api
)
from src.recommender.engine import load_data, recommend_games
from src.recommender.bgg_api import fetch_bgg_collection

def render_app():
    """Main rendering entrypoint for MeepleMind Streamlit Application."""
    # Set page configuration
    st.set_page_config(
        page_title="MeepleMind - Board Game Recommender",
        page_icon="🎲",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS theme
    apply_custom_styles()

    # Check if FastAPI backend service is running
    backend_active = is_backend_online()

    # Load dataset & metadata
    try:
        if backend_active:
            metadata_dict, categories, mechanics, themes, all_names = get_catalog_metadata()
            total_games = metadata_dict['total_games']
            total_mechanics = metadata_dict['total_mechanics']
            total_themes = metadata_dict['total_themes']
        else:
            data = load_data()
            df = data['metadata']
            categories = data['categories']
            mechanics = sorted(data['mechanics'])
            themes = sorted(data['themes'])
            all_names = sorted(df['Name'].tolist())
            total_games = len(df)
            total_mechanics = len(mechanics)
            total_themes = len(themes)
    except Exception as e:
        st.error(f"Failed to load dataset metadata: {e}.")
        st.stop()

    # Hero Header Banner
    render_hero_header()

    # Display Architecture Status Badge
    if backend_active:
        st.caption("🟢 **System Architecture:** Decoupled Mode — Streamlit Frontend connected to FastAPI Backend REST API (`http://localhost:8000`)")
    else:
        st.caption("🟡 **System Architecture:** Monolithic Direct Mode (FastAPI Backend Server on `http://localhost:8000` is offline)")

    # Initialize Session States
    if 'liked_games' not in st.session_state:
        st.session_state.liked_games = []
    if 'bgg_library' not in st.session_state:
        st.session_state.bgg_library = []
    if 'bgg_username' not in st.session_state:
        st.session_state.bgg_username = ""

    # Sidebar Controls
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
        
        # Show active complexity labels based on slider selection
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
            st.session_state.bgg_library = []
            st.session_state.bgg_username = ""
            st.rerun()

    # Main Body: Game Selection
    st.markdown("### 1. Select Board Games You Enjoy")
    st.caption("Tell us what games you love, and we will find others with similar mechanics and themes.")

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
        
        if st.session_state.liked_games:
            if st.button("🗑️ Clear My List", key="clear_manual"):
                st.session_state.liked_games = []
                st.rerun()

    with tab_bgg_import:
        st.markdown("##### Sync with your BoardGameGeek Account")
        st.caption("Enter your BGG username to pull games you own directly from the database.")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            bgg_username = st.text_input("BGG Username", placeholder="e.g. portos", key="bgg_username_input")
        with col2:
            st.write("") # Spacer
            st.write("")
            fetch_btn = st.button("🔄 Sync BGG Collection", use_container_width=True)
            
        if fetch_btn and bgg_username.strip():
            with st.spinner("Connecting to BGG XML API..."):
                if backend_active:
                    success, error_msg, matched = sync_bgg_collection_api(bgg_username)
                else:
                    success, error_msg, matched = fetch_bgg_collection(bgg_username, all_names)
                
                if success:
                    if matched:
                        st.session_state.bgg_library = matched
                        st.session_state.bgg_username = bgg_username.strip()
                        st.success(f"Successfully synced **{len(matched)}** games from **{bgg_username}**'s BGG collection!")
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        st.warning("Successfully connected, but no owned games in BGG matched our 22k game catalog.")
                else:
                    st.error("User not found. Make sure the username is correct and your collection is set to public.")

        exclude_bgg_owned = False
        use_profile_similarity = False
        
        if st.session_state.bgg_library:
            st.markdown("---")
            st.markdown(f"✅ **BGG library synced for: `{st.session_state.bgg_username}`** ({len(st.session_state.bgg_library)} games matched)")
            
            # Exclude checkbox
            exclude_bgg_owned = st.checkbox(
                "🚫 Exclude Owned Games from suggestions",
                value=True,
                help="Filter out all games in your synced BGG collection from candidate recommendations.",
                key="exclude_bgg_owned_checkbox"
            )
            
            # Toggle between seed matching vs profile-wide matching
            rec_basis = st.radio(
                "🎯 Recommendation Basis:",
                options=["Specific seed games (select below)", "Entire synced collection (profile-wide matching)"],
                index=0,
                help="Choose whether to recommend based on specific games or analyze your entire collection using profile similarity.",
                key="rec_basis_radio"
            )
            
            selected_bgg_seeds = []
            if rec_basis.startswith("Specific"):
                selected_bgg_seeds = st.multiselect(
                    "Select games from your collection to base recommendations on:",
                    options=st.session_state.bgg_library,
                    default=[g for g in st.session_state.liked_games if g in st.session_state.bgg_library],
                    key="bgg_seeds_multiselect"
                )
                use_profile_similarity = False
            else:
                selected_bgg_seeds = st.session_state.bgg_library
                use_profile_similarity = True
                
            manual_seeds = [g for g in st.session_state.liked_games if g not in st.session_state.bgg_library]
            st.session_state.liked_games = list(dict.fromkeys(manual_seeds + selected_bgg_seeds))

    # Display Current Liked List
    if st.session_state.liked_games and not use_profile_similarity:
        st.markdown("##### **Your Current Liked List:**")
        liked_html = " ".join(f'<span class="badge badge-similarity">🏷️ {item}</span>' for item in st.session_state.liked_games)
        st.markdown(liked_html, unsafe_allow_html=True)
    elif use_profile_similarity:
        st.markdown("##### **Recommending based on Profile-Wide BGG Library Match**")

    st.markdown("---")

    # Execute Recommendations
    if backend_active:
        recs = fetch_recommendations_api(
            selected_names=st.session_state.liked_games,
            player_count_range=player_count_range,
            playtime_option=playtime_option,
            complexity_range=complexity_range,
            selected_cats=selected_cats,
            selected_mechs=selected_mechs,
            selected_themes=selected_themes,
            exclude_names=st.session_state.bgg_library if exclude_bgg_owned else None,
            use_profile_similarity=use_profile_similarity,
            top_n=5
        )
    else:
        recs = recommend_games(
            selected_names=st.session_state.liked_games,
            player_count_range=player_count_range,
            playtime_option=playtime_option,
            complexity_range=complexity_range,
            selected_cats=selected_cats,
            selected_mechs=selected_mechs,
            selected_themes=selected_themes,
            exclude_names=st.session_state.bgg_library if exclude_bgg_owned else None,
            use_profile_similarity=use_profile_similarity,
            top_n=5
        )

    # Display Recommendations
    if recs:
        st.markdown(f"### ✨ Top Recommendations ({len(recs)} games found)")
        st.caption("Ranked by combining feature similarity (80%) and board game popularity/rating (20%).")
        
        for rec in recs:
            render_game_card(rec, st.session_state.liked_games)
    else:
        st.info("No games match your selected criteria. Try adjusting your player count, playtime, or complexity filters, or select different liked games!")

    # Dataset Schema Accordion Footer
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
        m_col1.metric("Total Board Games", f"{total_games:,}")
        m_col2.metric("Total Mechanics Mapped", f"{total_mechanics}")
        m_col3.metric("Total Themes Mapped", f"{total_themes}")
