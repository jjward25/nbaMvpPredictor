import sys
import pandas as pd
import os
from nba_api.stats.endpoints import leagueleaders

sys.stdout.reconfigure(encoding='utf-8')

# Define the seasons range from "2009-10" to the current season
seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(2009, 2024)]

# Initialize an empty DataFrame to hold the final results
players_df = pd.DataFrame()

# Loop through each season to retrieve the top 5 and bottom 15 players by points
for season in seasons:
    # Retrieve league leaders for the given season
    season_leaders = leagueleaders.LeagueLeaders(season=season)
    season_leaders_df = season_leaders.get_data_frames()[0]
    
    # Filter to get the top 5 players by points (PTS)
    top_players = season_leaders_df.nlargest(50, 'EFF')[['PLAYER_ID', 'PLAYER', 'TEAM','GP','PTS','REB','AST','EFF']]
    top_players['SEASON'] = season
    #top_players['RANK'] = 'Top 25'
    
    # Filter to get the bottom 15 players by points (PTS)
    #bottom_players = season_leaders_df.nsmallest(15, 'EFF')[['PLAYER_ID', 'PLAYER', 'TEAM', 'PTS','GP','FGA','FG_PCT','FG3A','FG3_PCT','REB','AST','STL','BLK','TOV','EFF','AST_TOV','STL_TOV']]
    #bottom_players['SEASON'] = season
    #bottom_players['RANK'] = 'Bottom 15'
    
    # Concatenate top and bottom players for the current season
    #season_df = pd.concat([top_players, bottom_players], ignore_index=True)
    
    # Append the current season's data to the final DataFrame
    #players_df = pd.concat([players_df, season_df], ignore_index=True)
    players_df = pd.concat([players_df, top_players], ignore_index=True)

# Output the final DataFrame containing the top 5 and bottom 15 players per season by points
print(players_df)
players_df.to_clipboard()

# Save the DataFrame to a CSV file
absolute_path = os.path.dirname(__file__)
filename = 'players50.csv'
file_path = absolute_path+'/'+filename
players_df.to_csv(file_path, index=False)