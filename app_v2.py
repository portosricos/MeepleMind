import json
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="ShopSmart Recommender",
    page_icon="🛒",
    layout="wide",             
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_rules():
    with open('association_rules.json', 'r') as f:
        data = json.load(f)
    return data

data = load_rules()
ALL_ITEMS = data['all_items']               
CATEGORIES = data['item_categories']      
RULES = data['rules']                       
META = data['metadata']                     

def get_recommendations(basket_items):
    recommendations = {}   

    for rule in RULES:
        antecedents = set(rule['antecedents'])
        consequents = set(rule['consequents'])

        if antecedents.issubset(basket_items):
            for item in consequents:
                if item not in basket_items:
                    if item not in recommendations or rule['lift'] > recommendations[item]['lift']:
                        recommendations[item] = {
                            'confidence': rule['confidence'],
                            'lift': rule['lift'],
                            'because': sorted(list(antecedents)),
                        }

    result = []
    for item, info in recommendations.items():
        result.append({
            'item': item,
            'confidence': info['confidence'],
            'lift': info['lift'],
            'because': info['because'],
        })

    result.sort(key=lambda x: x['lift'], reverse=True)
    return result

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .rec-card { background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border: 1px solid #bbf7d0; border-radius: 12px; padding: 1rem 1.2rem; margin-bottom: 0.7rem; transition: transform 0.15s, box-shadow 0.15s; }
    .rec-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
    .rec-item { font-size: 1.1rem; font-weight: 600; color: #166534; margin-bottom: 0.3rem; }
    .rec-meta { font-size: 0.82rem; color: #6b7280; line-height: 1.5; }
    .rec-badge { display: inline-block; background: #dcfce7; color: #166534; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; margin-right: 0.4rem; }
    .rec-badge-lift { background: #fef3c7; color: #92400e; }
    .basket-item { display: inline-flex; align-items: center; gap: 0.3rem; background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; padding: 0.35rem 0.7rem; border-radius: 8px; font-size: 0.9rem; font-weight: 500; margin: 0.2rem; }
    .stat-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 0.8rem 1rem; text-align: center; }
    .stat-num { font-size: 1.5rem; font-weight: 700; color: #1e293b; }
    .stat-label { font-size: 0.75rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
    .divider { height: 1px; background: #e2e8f0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🛒 Your Basket")
    
    if 'basket' not in st.session_state:
        st.session_state.basket = set()

    # --- RESTORED CATEGORY LOGIC ---
    # Extract unique categories from our dynamic dictionary
    unique_categories = sorted(set(CATEGORIES.values()))
    
    selected_category = st.selectbox(
        "Filter by category",
        options=["All Categories"] + unique_categories,
    )

    search_query = st.text_input("🔍 Search items", placeholder="Type to search...")

    filtered_items = ALL_ITEMS.copy()

    # Apply category filter
    if selected_category != "All Categories":
        filtered_items = [item for item in filtered_items if CATEGORIES.get(item) == selected_category]

    # Apply search filter
    if search_query:
        query_lower = search_query.lower()
        filtered_items = [item for item in filtered_items if query_lower in item.lower()]

    if filtered_items:
        st.caption(f"Showing {len(filtered_items)} items:")
        for item in filtered_items:
            if item in st.session_state.basket:
                st.button(f"✓ {item}", key=f"item_{item}", disabled=True, use_container_width=True)
            else:
                if st.button(f"＋ {item}", key=f"item_{item}", use_container_width=True):
                    st.session_state.basket.add(item)
                    st.rerun()   
    else:
        st.info("No items match your search.")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(f"**Basket ({len(st.session_state.basket)} items)**")

    if st.session_state.basket:
        for item in sorted(st.session_state.basket):
            col1, col2 = st.columns([4, 1])
            col1.markdown(f"• {item}")
            if col2.button("✕", key=f"remove_{item}"):
                st.session_state.basket.discard(item)
                st.rerun()

        if st.button("🗑️ Clear basket", use_container_width=True):
            st.session_state.basket = set()
            st.rerun()
    else:
        st.caption("Your basket is empty. Add items to get recommendations!")


st.markdown("# 🛍️ ShopSmart Recommender")
st.markdown("*Add items to your basket → get personalized recommendations based on what other customers buy together.*")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{META["num_transactions"]:,}</div><div class="stat-label">Transactions</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(ALL_ITEMS)}</div><div class="stat-label">Products</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="stat-box"><div class="stat-num">{META["num_rules"]}</div><div class="stat-label">Rules</div></div>', unsafe_allow_html=True)
with col4:
    # Extra dynamic stat: Total number of unique categories
    st.markdown(f'<div class="stat-box"><div class="stat-num">{len(unique_categories)}</div><div class="stat-label">Categories</div></div>', unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

if st.session_state.basket:
    st.markdown("### 🧺 Your current basket")
    basket_html = " ".join(f'<span class="basket-item">🏷️ {item}</span>' for item in sorted(st.session_state.basket))
    st.markdown(basket_html, unsafe_allow_html=True)
    st.markdown("")

    recs = get_recommendations(st.session_state.basket)

    if recs:
        st.markdown(f"### ✨ Recommended for you ({len(recs)} suggestions)")
        for rec in recs:
            st.markdown(f"""
            <div class="rec-card">
                <div class="rec-item">🏷️ {rec['item']}</div>
                <div class="rec-meta">
                    <span class="rec-badge">Confidence: {int(rec['confidence'] * 100)}%</span>
                    <span class="rec-badge rec-badge-lift">Lift: {rec['lift']:.1f}x</span><br>
                    Because you added: <strong>{', '.join(rec['because'])}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("")
        rec_names = [r['item'] for r in recs]
        selected_rec = st.selectbox("Select an item to add", options=["— Choose —"] + rec_names, label_visibility="collapsed")
        if selected_rec != "— Choose —":
            if st.button(f"Add {selected_rec} to basket"):
                st.session_state.basket.add(selected_rec)
                st.rerun()
    else:
        st.info("No recommendations found. Try adding more items!")
else:
    st.markdown("### 👈 Add items from the sidebar to get started")
    st.markdown(f"The recommendations come from **association rules** mined from {META['num_transactions']:,} real shopping transactions.")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.caption(f"Powered by Apriori algorithm · {META['num_transactions']:,} transactions · {META['num_rules']} rules")

# ============================================================
# 7.5. RULE EXPLORER (ACCORDION)
# ============================================================
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("### 📚 Rule Explorer")
st.caption("Curious about the engine? Browse all the raw association rules below.")

# st.expander creates the accordion!
with st.expander("🔍 View and Search All Rules"):
    
    # 1. Extract all unique items that appear as antecedents
    unique_antecedents = sorted(list(set(
        item for rule in RULES for item in rule['antecedents']
    )))

    # 2. Add a dropdown filter for the antecedents
    filter_ant = st.selectbox(
        "Filter rules by Antecedent (If you buy...)", 
        options=["— Show All —"] + unique_antecedents
    )

    # 3. Filter the rules list based on the dropdown selection
    filtered_rules = RULES
    if filter_ant != "— Show All —":
        filtered_rules = [r for r in RULES if filter_ant in r['antecedents']]

    # 4. Format the raw JSON rules into a clean list of dictionaries for the table
    display_data = []
    for r in filtered_rules:
        display_data.append({
            "If you buy... (Antecedents)": ", ".join(r['antecedents']),
            "...you also buy (Consequents)": ", ".join(r['consequents']),
            "Confidence": f"{r['confidence'] * 100:.0f}%",
            "Lift": f"{r['lift']:.2f}x"
        })

    # 5. Display as an interactive dataframe
    if display_data:
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No rules found for that selection.")