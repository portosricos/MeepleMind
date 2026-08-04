import numpy as np
import pandas as pd
import pickle
import os
from src.utils.config import PROCESSED_DATA_PATH

_DATA_CACHE = None

def load_data():
    """Load preprocessed board game metadata and feature matrix from pickle file."""
    global _DATA_CACHE
    if _DATA_CACHE is not None:
        return _DATA_CACHE
        
    if not os.path.exists(PROCESSED_DATA_PATH):
        raise FileNotFoundError(f"Processed BGG data pkl not found at {PROCESSED_DATA_PATH}. Run scripts/train_recommender.py first.")
        
    with open(PROCESSED_DATA_PATH, 'rb') as f:
        _DATA_CACHE = pickle.load(f)
        
    return _DATA_CACHE

def recommend_games(selected_names, player_count_range=None, playtime_option=None, complexity_range=None, 
                    selected_cats=None, selected_mechs=None, selected_themes=None, exclude_names=None, 
                    use_profile_similarity=False, top_n=5):
    """
    selected_names: List of names of games liked by the user
    player_count_range: Tuple (min_players, max_players), e.g. (2, 4)
    playtime_option: Str, 'Short (< 30 min)', 'Medium (30 - 60 min)', 'Long (60 - 120 min)', 'Epic (120 - 200 min)', 'Legendary (200+ min)'
    complexity_range: Tuple (min_weight, max_weight), e.g. (1.8, 3.2)
    selected_cats: List of categories to filter on
    selected_mechs: List of mechanics to filter on
    selected_themes: List of themes to filter on
    exclude_names: List of names to explicitly exclude from candidate recommendations
    use_profile_similarity: If True, calculates pairwise similarity to each game in user's profile and takes top matching averages.
    top_n: Number of recommendations to return
    """
    data = load_data()
    df = data['metadata']
    features_df = data['features']
    feature_cols = data['feature_cols']
    
    # 1. Map selected names to their BGGIds and index rows
    selected_ids = []
    selected_indices = []
    for name in selected_names:
        matches = df[df['Name'].str.lower() == name.lower()]
        if not matches.empty:
            selected_ids.append(matches.iloc[0]['BGGId'])
            selected_indices.append(matches.index[0])
            
    # 2. Start with all games as candidates, then apply filters
    candidates_mask = np.ones(len(df), dtype=bool)
    
    # Exclude games the user already selected
    if selected_indices:
        candidates_mask[selected_indices] = False
        
    # Exclude games in the custom exclusion list (e.g. user's BGG library)
    if exclude_names:
        # Bulk match case-insensitively for performance
        exclude_names_set = {n.lower() for n in exclude_names}
        exclude_mask = df['Name'].str.lower().isin(exclude_names_set)
        exclude_indices = df[exclude_mask].index.tolist()
        if exclude_indices:
            candidates_mask[exclude_indices] = False
        
    # Filter by player count range: check if candidate range overlaps with requested range
    if player_count_range is not None:
        req_min, req_max = player_count_range
        # Data cleaning check: Exclude games with invalid player counts (<= 0)
        candidates_mask &= (df['MinPlayers'] > 0) & (df['MaxPlayers'] > 0)
        candidates_mask &= (df['MinPlayers'] <= req_max) & (df['MaxPlayers'] >= req_min)
        
    # Filter by playtime options
    if playtime_option and playtime_option != "Any Duration":
        # Data cleaning check: Exclude games with invalid playtimes (<= 0)
        candidates_mask &= (df['MaxPlaytime'] > 0)
        if playtime_option == "Short (< 30 min)":
            candidates_mask &= (df['MaxPlaytime'] < 30)
        elif playtime_option == "Medium (30 - 60 min)":
            candidates_mask &= (df['MaxPlaytime'] >= 30) & (df['MaxPlaytime'] <= 60)
        elif playtime_option == "Long (60 - 120 min)":
            candidates_mask &= (df['MaxPlaytime'] > 60) & (df['MaxPlaytime'] <= 120)
        elif playtime_option == "Epic (120 - 200 min)":
            candidates_mask &= (df['MaxPlaytime'] > 120) & (df['MaxPlaytime'] <= 200)
        elif playtime_option == "Legendary (200+ min)":
            candidates_mask &= (df['MaxPlaytime'] > 200)
        
    # Filter by custom complexity range
    if complexity_range is not None:
        min_w, max_w = complexity_range
        # Data cleaning check: Exclude games with invalid complexity (<= 0)
        candidates_mask &= (df['GameWeight'] > 0)
        candidates_mask &= (df['GameWeight'] >= min_w) & (df['GameWeight'] <= max_w)
        
    # Filter by categories
    if selected_cats:
        cat_mask = np.zeros(len(df), dtype=bool)
        for cat in selected_cats:
            col = f"Cat:{cat}"
            if col in feature_cols:
                col_idx = feature_cols.index(col)
                cat_mask |= (features_df.iloc[:, col_idx] == 1).values
        candidates_mask &= cat_mask
        
    # Filter by mechanics
    if selected_mechs:
        mech_mask = np.zeros(len(df), dtype=bool)
        for mech in selected_mechs:
            if mech in feature_cols:
                col_idx = feature_cols.index(mech)
                mech_mask |= (features_df.iloc[:, col_idx] == 1).values
        candidates_mask &= mech_mask
        
    # Filter by themes
    if selected_themes:
        theme_mask = np.zeros(len(df), dtype=bool)
        for theme in selected_themes:
            if theme in feature_cols:
                col_idx = feature_cols.index(theme)
                theme_mask |= (features_df.iloc[:, col_idx] == 1).values
        candidates_mask &= theme_mask
        
    candidate_indices = np.where(candidates_mask)[0]
    
    if len(candidate_indices) == 0:
        return []
        
    # 3. Calculate similarity score
    sim_scores = np.zeros(len(df))
    
    if selected_indices:
        selected_features = features_df.values[selected_indices]
        candidate_features = features_df.values[candidate_indices]
        
        if use_profile_similarity:
            # Pairwise cosine similarity between candidates (N) and user's profile games (M)
            user_norms = np.linalg.norm(selected_features, axis=1)
            user_norms[user_norms == 0] = 1.0
            
            candidate_norms = np.linalg.norm(candidate_features, axis=1)
            candidate_norms[candidate_norms == 0] = 1.0
            
            # shape (N, M)
            dot_products = np.dot(candidate_features, selected_features.T)
            pairwise_similarities = dot_products / (candidate_norms[:, None] * user_norms[None, :])
            
            # Rank candidates by how closely they match their top 5 closest matches in the user's collection
            M = len(selected_indices)
            k = min(5, M)
            if k > 0:
                top_k_similarities = np.partition(pairwise_similarities, -k, axis=1)[:, -k:]
                sim_scores[candidate_indices] = np.mean(top_k_similarities, axis=1)
            else:
                sim_scores[candidate_indices] = 0.0
        else:
            user_vector = np.mean(selected_features, axis=0)
            user_norm = np.linalg.norm(user_vector)
            
            if user_norm > 0:
                candidate_norms = np.linalg.norm(candidate_features, axis=1)
                candidate_norms[candidate_norms == 0] = 1.0
                
                dot_products = np.dot(candidate_features, user_vector)
                cosine_similarities = dot_products / (user_norm * candidate_norms)
                
                sim_scores[candidate_indices] = cosine_similarities
            
    # 4. Integrate rating/popularity
    bayes_ratings = df['BayesAvgRating'].values
    min_b, max_b = 3.5, 8.5
    normalized_ratings = np.clip((bayes_ratings - min_b) / (max_b - min_b), 0.0, 1.0)
    
    final_scores = np.zeros(len(df))
    if selected_indices:
        final_scores[candidate_indices] = (sim_scores[candidate_indices] * 0.8) + (normalized_ratings[candidate_indices] * 0.2)
    else:
        final_scores[candidate_indices] = normalized_ratings[candidate_indices]
        
    # 5. Extract top recommendations
    top_candidate_indices = sorted(candidate_indices, key=lambda idx: final_scores[idx], reverse=True)[:top_n]
    
    results = []
    for idx in top_candidate_indices:
        game_row = df.iloc[idx]
        
        shared_categories = []
        shared_mechanics = []
        shared_themes = []
        
        if selected_indices:
            liked_cats = set(c for s_idx in selected_indices for c in df.iloc[s_idx]['Categories_List'])
            liked_mechs = set(m for s_idx in selected_indices for m in df.iloc[s_idx]['Mechanics_List'])
            liked_themes = set(t for s_idx in selected_indices for t in df.iloc[s_idx]['Themes_List'])
            
            shared_categories = list(liked_cats.intersection(game_row['Categories_List']))
            shared_mechanics = list(liked_mechs.intersection(game_row['Mechanics_List']))
            shared_themes = list(liked_themes.intersection(game_row['Themes_List']))
            
        results.append({
            'BGGId': int(game_row['BGGId']),
            'Name': str(game_row['Name']),
            'Description': str(game_row['Description']) if pd.notna(game_row['Description']) else '',
            'YearPublished': int(game_row['YearPublished']),
            'GameWeight': float(game_row['GameWeight']),
            'AvgRating': float(game_row['AvgRating']),
            'BayesAvgRating': float(game_row['BayesAvgRating']),
            'MinPlayers': int(game_row['MinPlayers']),
            'MaxPlayers': int(game_row['MaxPlayers']),
            'ComAgeRec': float(game_row['ComAgeRec']),
            'LanguageEase': float(game_row['LanguageEase']),
            'BestPlayers': str(game_row['BestPlayers']) if pd.notna(game_row['BestPlayers']) else '',
            'TotalEngagement': int(game_row['TotalEngagement']),
            'MaxPlaytime': float(game_row['MaxPlaytime']),
            'MinPlaytime': float(game_row['MinPlaytime']),
            'ImagePath': str(game_row['ImagePath']) if pd.notna(game_row['ImagePath']) else '',
            'Categories': list(game_row['Categories_List']),
            'Mechanics': list(game_row['Mechanics_List']),
            'Themes': list(game_row['Themes_List']),
            'Similarity': float(sim_scores[idx]) if selected_indices else 0.0,
            'Score': float(final_scores[idx]),
            'SharedCategories': shared_categories,
            'SharedMechanics': shared_mechanics,
            'SharedThemes': shared_themes
        })
        
    return results
