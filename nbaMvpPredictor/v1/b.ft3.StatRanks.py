import pandas as pd
from nba_api.stats.endpoints import playerprofilev2
import os
import time
import logging
import sys
from requests.exceptions import ReadTimeout, ConnectionError

# Configure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the players.csv file
absolute_path = os.path.dirname(__file__)
filename = 'players_with_mvp_googles.csv'
file_path = os.path.join(absolute_path, filename)
players_df = pd.read_csv(file_path)

# Remove unwanted columns
players_df = players_df.drop(['TEAM', 'PTS', 'FGA', 'FG_PCT', 'FG3A', 'FG3_PCT', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'AST_TOV', 'STL_TOV'], axis=1)

# Function to fetch SeasonRankingsRegularSeason data and filter by season
def fetch_player_ranks(player_id, season, retries=5):
    delay = 5  # Start with 5 seconds
    for attempt in range(retries):
        try:
            # Fetch profile data for the player
            profile_data_frames = playerprofilev2.PlayerProfileV2(player_id=player_id).get_data_frames()
            logging.info(f"Number of DataFrames returned for Player ID {player_id}: {len(profile_data_frames)}")

            # Log the shape and columns of all data frames
            for i, df in enumerate(profile_data_frames):
                #logging.info(f"DataFrame {i}: shape = {df.shape}, columns = {df.columns.tolist()}")
                if df.empty:
                    logging.warning(f"DataFrame {i} is empty.")
                elif any('RANK' in col for col in df.columns):
                    # Filter for the specific season
                    season_data = df[df['SEASON_ID'] == season]
                    if not season_data.empty:
                        logging.info(f"Fetched Season Rankings for Player ID {player_id}: {season_data.shape[0]} rows.")
                        return season_data
                    else:
                        logging.warning(f"No data found for season {season} in DataFrame {i} for Player ID {player_id}.")

            logging.warning(f"No SeasonRankingsRegularSeason data available for Player ID {player_id}.")
            return pd.DataFrame()

        except (ReadTimeout, ConnectionError) as e:
            logging.warning(f"Attempt {attempt + 1} failed for player ID {player_id}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
            delay *= 2  # Double the delay for the next attempt
            
    logging.error(f"Failed to fetch rankings data for player ID {player_id} after {retries} attempts.")
    return pd.DataFrame()


# Loop through each player and season in players_df to fetch and append ranking data
ranking_data = []
for index, row in players_df.iterrows():
    player_id = row['PLAYER_ID']
    season = row['SEASON']
    logging.info(f"Processing Player ID {player_id}, Season {season}.")
    
    season_ranking = fetch_player_ranks(player_id, season)
    
    if not season_ranking.empty:
        ranking_data.append(season_ranking)

    time.sleep(2)  # To avoid rate limits

# Concatenate all rankings data and merge with players_df on Player_ID and Season
if ranking_data:  # Only concatenate if there's data
    rankings_df = pd.concat(ranking_data, ignore_index=True)
    merged_df = pd.merge(players_df, rankings_df, how='left', left_on=['PLAYER_ID', 'SEASON'], right_on=['PLAYER_ID', 'SEASON_ID'])
else:
    logging.warning("No ranking data collected.")

# Save the updated DataFrame to a new CSV
merged_df.to_csv('players_with_mvp_and_rankings.csv', index=False)
logging.info(f"Data saved to 'players_with_mvp_and_rankings.csv' with {merged_df.shape[0]} rows.")
print(merged_df)
