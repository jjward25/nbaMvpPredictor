from nba_api.stats.static import players
from nba_api.stats.static import teams
from nba_api.stats.endpoints import playerawards, commonplayerinfo

players = players.get_players()
#teams = teams.get_teams()
#print(players)

# Basic Request
# player_info = commonplayerinfo.CommonPlayerInfo(player_id=2544,  timeout=100)
# print(player_info.get_data_frames()[0])

playerAwards = playerawards.PlayerAwards(player_id=2544)

awards_data = playerAwards.get_data_frames()[0]  # Access the first DataFrame
#print(awards_data)
#awards_data.to_clipboard(index=False)

playerData = commonplayerinfo.CommonPlayerInfo(player_id=2544, timeout=100).get_data_frames()[0]
print(playerData)
playerData.to_clipboard()