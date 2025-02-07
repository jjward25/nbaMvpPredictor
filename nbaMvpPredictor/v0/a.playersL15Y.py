import pandas as pd
from nba_api.stats.endpoints import commonallplayers
import time
import os

# Function to fetch player data with retries
def fetch_player_data(retries=3, timeout=60):
    for attempt in range(retries):
        try:
            return commonallplayers.CommonAllPlayers(timeout=timeout).get_data_frames()[0]
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(2)  # Wait before retrying
    return pd.DataFrame()  # Return an empty DataFrame after retries fail

# Fetch the player data
all_players_data = fetch_player_data()

# DataFrame to store all valid players
playerList = pd.DataFrame()

# Convert TO_YEAR to numeric
all_players_data['TO_YEAR'] = pd.to_numeric(all_players_data['TO_YEAR'], errors='coerce')

# Iterate over each player in the fetched player data
for index, player in all_players_data.iterrows():
    player_id = player['PERSON_ID']

    try:
        # Check if TO_YEAR exists and filter for players from 2009 onwards
        if 'TO_YEAR' in player:
            if player['TO_YEAR'] >= 2009:
                playerList = pd.concat([playerList, pd.DataFrame([player])], ignore_index=True)
    except Exception as e:
        print(f"Error processing player (ID: {player_id}): {e}")

# Display the playerList DataFrame
#print("Available columns in playerList:")
#print(playerList.columns.tolist())
columns_to_keep = ['PERSON_ID', 'DISPLAY_LAST_COMMA_FIRST', 'DISPLAY_FIRST_LAST', 'FROM_YEAR','TO_YEAR']
playerList2009 = playerList[columns_to_keep]
#print(playerList)


# Save the DataFrame to a CSV file
absolute_path = os.path.dirname(__file__)
filename = 'players_since_2009'
file_path = os.path.join(absolute_path, f'{filename}.csv')
try:
    playerList2009.to_csv(file_path, index=False, encoding='utf-8')
    print(f"Player list saved to CSV at {file_path}.")
except Exception as e:
    print(f"Error saving DataFrame to CSV: {e}")