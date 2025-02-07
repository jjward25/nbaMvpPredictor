import pandas as pd
import os
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo

# Get the list of players
all_players = players.get_players()

# Create an empty DataFrame to store valid player data
playerList = pd.DataFrame()

# Define retry parameters
max_retries = 3  # Maximum number of retries
retry_delay = 5  # Delay between retries in seconds

for player in all_players:
    player_id = player['id']  # Extract the player ID
    player_name = player['full_name']  # Get player's full name for logging
    attempts = 0  # Initialize attempts counter

    while attempts < max_retries:
        try:
            # Request player data
            playerData = commonplayerinfo.CommonPlayerInfo(player_id=player_id, timeout=100).get_data_frames()[0]
            
            # Ensure the 'TO_YEAR' column exists before filtering to only players active since 2009
            if 'TO_YEAR' in playerData.columns:
                validPlayer = playerData[playerData['TO_YEAR'] >= 2009]
            
                # Append to main DataFrame if there are valid players
                if not validPlayer.empty:
                    playerList = pd.concat([playerList, validPlayer], ignore_index=True)
            else:
                print(f"'TO_YEAR' column not found for player {player_name} (ID: {player_id})")
            
            break  # Exit retry loop if successful

        except Exception as e:
            attempts += 1
            print(f"Error processing player {player_name} (ID: {player_id}): {e}")
            if attempts < max_retries:
                print(f"Retrying... (Attempt {attempts}/{max_retries})")
                time.sleep(retry_delay)  # Wait before retrying

# Display the final player list
print(playerList)

# Save the DataFrame to a CSV file
absolute_path = os.path.dirname(__file__)
filename = 'player_list.csv'
file_path = absolute_path+'/'+{filename}+'.csv'
playerList.to_csv(file_path, index=False)

print(f"Player list saved to CSV and copied to clipboard.")
playerList.to_clipboard()