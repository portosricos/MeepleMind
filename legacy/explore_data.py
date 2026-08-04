import pandas as pd

games_path = './raw_data/games.csv'
mechanics_path = './raw_data/mechanics.csv'
themes_path = './raw_data/themes.csv'

games_df = pd.read_csv(games_path)
print("Games shape:", games_df.shape)
print("Games BGGId min/max:", games_df['BGGId'].min(), games_df['BGGId'].max())

try:
    mechanics_df = pd.read_csv(mechanics_path)
    print("Mechanics shape:", mechanics_df.shape)
    print("Mechanics columns (first 10):", list(mechanics_df.columns[:10]))
except Exception as e:
    print("Error reading mechanics:", e)

try:
    themes_df = pd.read_csv(themes_path)
    print("Themes shape:", themes_df.shape)
    print("Themes columns (first 10):", list(themes_df.columns[:10]))
except Exception as e:
    print("Error reading themes:", e)
