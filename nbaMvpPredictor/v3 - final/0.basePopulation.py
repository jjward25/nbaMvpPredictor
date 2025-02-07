import pandas as pd
from nba_api.stats.endpoints import leagueleaders
import time, logging, sys
from requests.exceptions import ReadTimeout, ConnectionError

# Configure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Columns to retrieve and transform
columns = ['PLAYER_ID', 'PLAYER', 'TEAM', 'GP', 'MIN', 'FGA', 'FG_PCT', 'REB', 'AST', 'PTS', 'EFF','TEAM_ID']
transformed_columns = ['MIN_per_game', 'FGA_per_game', 'REB_per_game', 'AST_per_game', 'PTS_per_game', 'EFF_per_game']

# Function to fetch the top 50 players by EFF for a given season
def fetch_season_leaders(season, retries=5):
    delay = 5  # Start with 5 seconds
    for attempt in range(retries):
        try:
            # Fetch data for top 50 EFF players for the season
            season_leaders = leagueleaders.LeagueLeaders(season=season, stat_category_abbreviation='EFF')
            season_df = season_leaders.get_data_frames()[0]
            
            # Filter to include only the top 50 players and select specified columns
            season_df = season_df[columns].head(50)
            
            # Calculate per-game statistics
            for col in ['MIN', 'FGA', 'REB', 'AST', 'PTS', 'EFF']:
                season_df[f"{col}_per_game"] = season_df[col] / season_df['GP']
            
            # Rank each player within the top 50 for each per-game metric
            for col in transformed_columns:
                season_df[f"{col}_rank"] = season_df[col].rank(ascending=False)

            # Rank each player within the top 50 for non per-game metrics
            for col in ['GP', 'MIN', 'FGA', 'FG_PCT', 'REB', 'AST', 'PTS', 'EFF']:
                season_df[f"{col}_rank"] = season_df[col].rank(ascending=False)
            
            # Add the season column for reference
            season_df['SEASON'] = season
            
            return season_df

        except (ReadTimeout, ConnectionError) as e:
            logging.warning(f"Attempt {attempt + 1} failed for season {season}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff for each retry

    logging.error(f"Failed to fetch data for season {season} after {retries} attempts.")
    return pd.DataFrame()

# Retrieve and concatenate data for the last 10 seasons
all_seasons_df = pd.DataFrame()
for year in range(2024, 2013, -1):  # Adjust range for desired seasons
    season = f"{year}-{str(year+1)[-2:]}"
    logging.info(f"Processing season {season}")
    
    season_df = fetch_season_leaders(season)
    
    if not season_df.empty:
        all_seasons_df = pd.concat([all_seasons_df, season_df], ignore_index=True)
    else:
        logging.warning(f"No data collected for season {season}")

# Save the resulting DataFrame to CSV
all_seasons_df.to_csv('allPlayersStats.csv', index=False)
logging.info(f"Data saved to 'allPlayersStats.csv' with {all_seasons_df.shape[0]} rows.")
print(all_seasons_df)
all_seasons_df.to_clipboard()
