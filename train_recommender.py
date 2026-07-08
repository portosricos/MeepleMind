import pandas as pd
import numpy as np
import os
import pickle

def preprocess_bgg_data():
    print("Starting BGG data preprocessing...")
    
    games_path = './raw_data/games.csv'
    mechanics_path = './raw_data/mechanics.csv'
    themes_path = './raw_data/themes.csv'
    
    # 1. Load datasets
    print("Loading datasets...")
    games_df = pd.read_csv(games_path)
    mechanics_df = pd.read_csv(mechanics_path)
    themes_df = pd.read_csv(themes_path)
    
    print(f"Original shapes -> Games: {games_df.shape}, Mechanics: {mechanics_df.shape}, Themes: {themes_df.shape}")
    
    # 2. Clean duplicates by BGGId
    games_df = games_df.drop_duplicates(subset=['BGGId'])
    mechanics_df = mechanics_df.drop_duplicates(subset=['BGGId'])
    themes_df = themes_df.drop_duplicates(subset=['BGGId'])
    
    print("Merging datasets on BGGId...")
    # 3. Merge datasets
    merged_df = games_df.merge(mechanics_df, on='BGGId', how='inner')
    merged_df = merged_df.merge(themes_df, on='BGGId', how='inner')
    
    print(f"Merged shape: {merged_df.shape}")
    
    # 4. Feature Engineering
    print("Performing feature engineering...")
    
    # Total Engagement (popularity proxy)
    merged_df['TotalEngagement'] = (
        merged_df['NumOwned'].fillna(0) + 
        merged_df['NumWant'].fillna(0) + 
        merged_df['NumWish'].fillna(0) + 
        merged_df['NumUserRatings'].fillna(0)
    )
    
    # Max Playtime (resolving missing values and ComMaxPlaytime vs MfgPlaytime)
    merged_df['MaxPlaytime'] = merged_df['ComMaxPlaytime'].replace(0, np.nan).fillna(merged_df['MfgPlaytime'])
    merged_df['MaxPlaytime'] = merged_df['MaxPlaytime'].fillna(30) # Default fallback
    
    # Min Playtime
    merged_df['MinPlaytime'] = merged_df['ComMinPlaytime'].replace(0, np.nan).fillna(merged_df['MfgPlaytime'])
    merged_df['MinPlaytime'] = merged_df['MinPlaytime'].fillna(30) # Default fallback
    
    # Handle descriptive nulls
    merged_df['Description'] = merged_df['Description'].fillna('No description available.')
    merged_df['ImagePath'] = merged_df['ImagePath'].fillna('')
    merged_df['ComAgeRec'] = merged_df['ComAgeRec'].fillna(merged_df['ComAgeRec'].median())
    merged_df['LanguageEase'] = merged_df['LanguageEase'].fillna(merged_df['LanguageEase'].median())
    
    # Ensure numerical columns are properly formatted
    merged_df['GameWeight'] = pd.to_numeric(merged_df['GameWeight'], errors='coerce').fillna(2.0)
    merged_df['AvgRating'] = pd.to_numeric(merged_df['AvgRating'], errors='coerce').fillna(5.0)
    merged_df['BayesAvgRating'] = pd.to_numeric(merged_df['BayesAvgRating'], errors='coerce').fillna(merged_df['AvgRating'])
    merged_df['MinPlayers'] = pd.to_numeric(merged_df['MinPlayers'], errors='coerce').fillna(1).astype(int)
    merged_df['MaxPlayers'] = pd.to_numeric(merged_df['MaxPlayers'], errors='coerce').fillna(4).astype(int)
    
    # 5. Extract Feature Categories for similarity
    # Get all category columns (Cat:*)
    cat_cols = [c for c in games_df.columns if c.startswith('Cat:')]
    
    # Get all mechanics columns (excluding BGGId)
    mech_cols = [c for c in mechanics_df.columns if c != 'BGGId']
    
    # Get all themes columns (excluding BGGId)
    theme_cols = [c for c in themes_df.columns if c != 'BGGId']
    
    feature_cols = cat_cols + mech_cols + theme_cols
    print(f"Total binary features for similarity: {len(feature_cols)} (Categories: {len(cat_cols)}, Mechanics: {len(mech_cols)}, Themes: {len(theme_cols)})")
    
    # 6. Build the final output structure
    metadata_cols = [
        'BGGId', 'Name', 'Description', 'YearPublished', 'GameWeight', 
        'AvgRating', 'BayesAvgRating', 'MinPlayers', 'MaxPlayers', 
        'ComAgeRec', 'LanguageEase', 'BestPlayers', 'TotalEngagement', 
        'MaxPlaytime', 'MinPlaytime', 'ImagePath'
    ]
    
    # Store lists of individual features as labels to display on the UI
    print("Extracting feature labels for UI display...")
    
    def get_labels(row, cols, prefix=""):
        return [c.replace(prefix, "") for c in cols if row[c] == 1]
        
    merged_df['Categories_List'] = merged_df.apply(lambda r: get_labels(r, cat_cols, "Cat:"), axis=1)
    merged_df['Mechanics_List'] = merged_df.apply(lambda r: get_labels(r, mech_cols), axis=1)
    merged_df['Themes_List'] = merged_df.apply(lambda r: get_labels(r, theme_cols), axis=1)
    
    # Output structure
    output_df = merged_df[metadata_cols + ['Categories_List', 'Mechanics_List', 'Themes_List']].copy()
    
    # Ensure binary features are boolean/int8 to keep pickle footprint tiny
    binary_matrix = merged_df[feature_cols].astype(np.int8)
    
    output_data = {
        'metadata': output_df,
        'features': binary_matrix,
        'feature_cols': feature_cols,
        'categories': [c.replace("Cat:", "") for c in cat_cols],
        'mechanics': mech_cols,
        'themes': theme_cols
    }
    
    output_file = './processed_games.pkl'
    print(f"Saving preprocessed data to {output_file}...")
    with open(output_file, 'wb') as f:
        pickle.dump(output_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        
    print("Preprocessing completed successfully!")

if __name__ == "__main__":
    preprocess_bgg_data()
