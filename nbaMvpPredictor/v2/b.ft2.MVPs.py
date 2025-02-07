import pandas as pd
from nba_api.stats.endpoints import playerawards
import os
import time
import logging
from requests.exceptions import ReadTimeout, ConnectionError

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the players.csv file
absolute_path = os.path.dirname(__file__)
filename = 'playersRanks.csv'
file_path = os.path.join(absolute_path, filename)
players_df = pd.read_csv(file_path)
players_df = players_df.drop(columns=['LEAGUE_ID','SEASON_ID','TEAM_ID','TEAM_ABBREVIATION','PLAYER_AGE','GP_y','GS','RANK_FGM','RANK_FGA','RANK_FG_PCT','RANK_FG3M','RANK_FG3A','RANK_FG3_PCT','RANK_FTM','RANK_FTA','RANK_FT_PCT','RANK_OREB','RANK_DREB'],errors='ignore')

# Add an MVP column initialized to 0
players_df['MVP'] = 0

def get_player_awards(player_id, season, retries=5):
    delay = 5  # Start with 5 seconds
    for attempt in range(retries):
        try:
            # Fetch player awards data
            awards_data = playerawards.PlayerAwards(player_id=player_id).get_data_frames()[0]
            return awards_data
        except (ReadTimeout, ConnectionError) as e:
            logging.warning(f"Attempt {attempt + 1} failed for player ID {player_id}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
            delay *= 2  # Double the delay for the next attempt
    logging.error(f"Failed to fetch awards data for player ID {player_id} after {retries} attempts.")
    return pd.DataFrame()  # Return an empty DataFrame if all attempts fail

# Loop through each player and check for MVP award
for index, row in players_df.iterrows():
    player_id = row['PLAYER_ID']
    season = row['SEASON']
    
    # Get awards data with retry logic
    awards_data = get_player_awards(player_id, season)

    # Check if there's an MVP award for the player in the given season
    if not awards_data.empty:
        mvp_award = awards_data[
            (awards_data['DESCRIPTION'] == 'NBA Most Valuable Player') & 
            (awards_data['SEASON'] == season)
        ]
        if not mvp_award.empty:
            players_df.at[index, 'MVP'] = 1

# Save the updated DataFrame to a new CSV
output_filename = 'playersMVP.csv'
output_path = os.path.join(absolute_path, output_filename)
players_df.to_csv(output_path, index=False)

logging.info("Updated DataFrame with MVP column saved to: %s", output_filename)
