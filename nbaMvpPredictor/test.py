import pandas as pd
import os
from nba_api.stats.endpoints import leagueleaders

#data = playercareerstats.PlayerCareerStats(player_id=2544)
#data_frames = data.get_data_frames()
#print(data_frames)

import sys
import pandas as pd
from nba_api.stats.endpoints import playerawards, teamyearbyyearstats

sys.stdout.reconfigure(encoding='utf-8')

## League Leaders
#season_leaders = leagueleaders.LeagueLeaders(season='2024-25')
#season_leaders_df = season_leaders.get_data_frames()[0]
#print(season_leaders_df)
#season_leaders_df.to_clipboard()

## Awards
#awards = playerawards.PlayerAwards(player_id=2544).get_data_frames()
#print(awards)
#awards[0].to_clipboard()

#from nba_api.stats.endpoints import playerprofilev2
#profile_data = playerprofilev2.PlayerProfileV2(player_id=2544).get_data_frames()[2]
#print(profile_data)
#profile_data.to_clipboard()

## Team Stats
teams = teamyearbyyearstats.TeamYearByYearStats(team_id='1610612743')
teams_df = teams.get_data_frames()[0]
print(teams_df)
teams_df.to_clipboard()