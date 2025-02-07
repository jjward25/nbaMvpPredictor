import pandas as pd
from nba_api.stats.endpoints import teamyearbyyearstats
import os, sys, time, logging
from requests.exceptions import ReadTimeout, ConnectionError

# Configure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the playersMVP.csv file
absolute_path = os.path.dirname(__file__)
filename = 'playersMVP.csv'
file_path = os.path.join(absolute_path, filename)
players_df = pd.read_csv(file_path)

# Define function to fetch team data with retry logic
def fetch_team_stats(team_id, retries=5):
    delay = 5  # Start with 5 seconds
    for attempt in range(retries):
        try:
            # Retrieve team year-by-year stats
            team_stats = teamyearbyyearstats.TeamYearByYearStats(team_id=team_id).get_data_frames()[0]
            return team_stats
        except (ReadTimeout, ConnectionError) as e:
            logging.warning(f"Attempt {attempt + 1} failed for team ID {team_id}: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff for each retry

    logging.error(f"Failed to fetch data for team ID {team_id} after {retries} attempts.")
    return pd.DataFrame()

# Dictionary to cache team stats data by team_id
team_stats_cache = {}

# List to store updated player rows with team data
updated_rows = []

# Iterate through each player row in the dataframe
for index, row in players_df.iterrows():
    team_id = row['TEAM_ID']
    season = row['SEASON']

    # Check if team data is already fetched for this team_id
    if team_id not in team_stats_cache:
        team_stats_cache[team_id] = fetch_team_stats(team_id)

    # Get team stats for the specified season
    team_data = team_stats_cache[team_id]
    season_team_data = team_data[team_data['YEAR'] == season]

    # If matching season data is found, add required columns
    if not season_team_data.empty:
        row['CONF_RANK'] = season_team_data.iloc[0]['CONF_RANK']
        row['WIN_PCT'] = season_team_data.iloc[0]['WIN_PCT']
        row['PTS_RANK'] = season_team_data.iloc[0]['PTS_RANK']
    else:
        logging.warning(f"No matching team data for team ID {team_id} in season {season}")
        row['CONF_RANK'], row['WIN_PCT'], row['PTS_RANK'] = None, None, None

    # Append updated row to list
    updated_rows.append(row)

# Create a new DataFrame with the updated rows
updated_df = pd.DataFrame(updated_rows)

# Save the updated DataFrame to a new CSV file
updated_df.to_csv('playersMvpTeams.csv', index=False)
logging.info("Data saved to 'playersMVP_with_team_data.csv'")
print(updated_df)
