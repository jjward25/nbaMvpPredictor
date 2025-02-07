import re
import pandas as pd
import os, sys, time
from pytrends.request import TrendReq
sys.stdout.reconfigure(encoding='utf-8')

# Load the CSV file
project_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = "players_with_mvp.csv"
csv_path = os.path.join(project_directory, csv_file)
df = pd.read_csv(csv_path)

# Initialize Pytrends
pytrends = TrendReq(hl='en-US')

# Define a function to sanitize and fetch Google Trends data
def fetch_google_trends(player_name, season):
    # Remove special characters for consistency
    clean_name = re.sub(r"[^a-zA-Z\s]", "", player_name)
    
    # Determine the start and end dates based on the season
    year_start, year_end = season.split('-')
    start_date = f"{year_start}-10-01"  # October 1 of the start year
    end_date = f"20{year_end}-06-30"  # June 30 of the end year with '20' prefix
    
    # Add "NBA" to the player name for disambiguation
    search_term = f"{clean_name} NBA"
    
    try:
        pytrends.build_payload([search_term], timeframe=f"{start_date} {end_date}")
        data = pytrends.interest_over_time()
        return data[search_term].sum() if not data.empty else 0
    except Exception as e:
        print(f"Error fetching data for {player_name} from {start_date} to {end_date}: {e}")
        return None

# Loop through the DataFrame and fetch data
google_search_mentions = []
for index, row in df.iterrows():
    mentions = fetch_google_trends(row['PLAYER'], row['SEASON'])
    google_search_mentions.append(mentions)
    time.sleep(2)  # Delay for 2 seconds between requests to avoid hitting rate limits

# Add the new data to the DataFrame
df['google_search_mentions'] = google_search_mentions

# Save the updated DataFrame to a new CSV
df.to_csv('players_with_mvp_googles.csv', index=False)
print(df)
df.to_clipboard()
