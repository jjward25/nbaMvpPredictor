import pandas as pd
import os
import time
from nba_api.stats.endpoints import playercareerstats
from requests.exceptions import ReadTimeout

# Checking if the base player list has been created.
absolute_path = os.path.dirname(__file__)
filename = 'players_since_2009'
csv_file_path = os.path.join(absolute_path, f'{filename}.csv')
script_to_run = 'a.playersL15Y.py'  # The script to create the CSV if it does not exist

# Initialize an empty DataFrame to store the results
final_df = pd.DataFrame(columns=[
    'PERSON_ID', 'DISPLAY_FIRST_LAST', 'SEASON_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE', 
    'GP', 'GS', 'RANK_MIN', 'RANK_FGM', 'RANK_FGA', 'RANK_FG_PCT', 'RANK_FG3M', 'RANK_FG3A', 
    'RANK_FG3_PCT', 'RANK_FTM', 'RANK_FTA', 'RANK_FT_PCT', 'RANK_OREB', 'RANK_DREB', 'RANK_REB', 
    'RANK_AST', 'RANK_STL', 'RANK_BLK', 'RANK_TOV', 'RANK_PTS', 'RANK_EFF'
])

# Check if the CSV file exists
if not os.path.exists(csv_file_path):
    print(f"{csv_file_path} does not exist. Running {script_to_run} to create it.")
else:
    data = pd.read_csv(csv_file_path)

    for index, player in data.iterrows():
        player_id = player['PERSON_ID']
        display_name = player['DISPLAY_FIRST_LAST']
        
        retry_count = 0
        success = False

        while not success and retry_count < 3:
            try:
                # Fetch player profile data using a valid player ID
                player_profile = playercareerstats.PlayerCareerStats(player_id, timeout=30)
                data_frames = player_profile.get_data_frames()
                pdata = None

                # Identify the regular season dataset
                for df in data_frames:
                    if "RANK_MIN" in df.columns:
                        if pdata is None or len(df) > len(pdata):
                            pdata = df

                # Process pdata if it contains data
                if pdata is not None and not pdata.empty:
                    pdata['SEASON_YEAR'] = pdata['SEASON_ID'].str[:4]
                    filtered_data = pdata[(pdata['SEASON_YEAR'].astype(int) >= 2009) & (pdata['RANK_PTS'] > 50)].copy()
                    filtered_data.reset_index(drop=True, inplace=True)

                    # Create a new DataFrame that includes player info and filtered stats
                    combined_data = pd.DataFrame({
                        'PERSON_ID': player_id,
                        'DISPLAY_FIRST_LAST': display_name,
                        'SEASON_ID': filtered_data['SEASON_ID'],
                        'TEAM_ID': filtered_data['TEAM_ID'],
                        'TEAM_ABBREVIATION': filtered_data['TEAM_ABBREVIATION'],
                        'PLAYER_AGE': filtered_data['PLAYER_AGE'],
                        'GP': filtered_data['GP'],
                        'GS': filtered_data['GS'],
                        'RANK_MIN': filtered_data['RANK_MIN'],
                        'RANK_FGM': filtered_data['RANK_FGM'],
                        'RANK_FGA': filtered_data['RANK_FGA'],
                        'RANK_FG_PCT': filtered_data['RANK_FG_PCT'],
                        'RANK_FG3M': filtered_data['RANK_FG3M'],
                        'RANK_FG3A': filtered_data['RANK_FG3A'],
                        'RANK_FG3_PCT': filtered_data['RANK_FG3_PCT'],
                        'RANK_FTM': filtered_data['RANK_FTM'],
                        'RANK_FTA': filtered_data['RANK_FTA'],
                        'RANK_FT_PCT': filtered_data['RANK_FT_PCT'],
                        'RANK_OREB': filtered_data['RANK_OREB'],
                        'RANK_DREB': filtered_data['RANK_DREB'],
                        'RANK_REB': filtered_data['RANK_REB'],
                        'RANK_AST': filtered_data['RANK_AST'],
                        'RANK_STL': filtered_data['RANK_STL'],
                        'RANK_BLK': filtered_data['RANK_BLK'],
                        'RANK_TOV': filtered_data['RANK_TOV'],
                        'RANK_PTS': filtered_data['RANK_PTS'],
                        'RANK_EFF': filtered_data['RANK_EFF']
                    })

                    # Append combined_data to final_df
                    final_df = pd.concat([final_df, combined_data], ignore_index=True)
                
                success = True  # Exit retry loop on success

            except ReadTimeout:
                retry_count += 1
                print(f"Timeout for player {display_name} (ID: {player_id}). Retrying {retry_count}/3...")
                time.sleep(5)  # Wait a few seconds before retrying

            except Exception as e:
                print(f"An error occurred for player {display_name} (ID: {player_id}): {e}")
                break  # Exit retry loop on non-timeout errors

# Display the resulting DataFrame or save to a CSV as needed
print(final_df)
# final_df.to_csv('filtered_player_stats.csv', index=False)


# Save the DataFrame to a CSV file
absolute_path = os.path.dirname(__file__)
filename = 'top50PTSlast15'
file_path = os.path.join(absolute_path, f'{filename}.csv')
try:
    final_df.to_csv(file_path, index=False, encoding='utf-8')
    print(f"Player list saved to CSV at {file_path}.")
except Exception as e:
    print(f"Error saving DataFrame to CSV: {e}")