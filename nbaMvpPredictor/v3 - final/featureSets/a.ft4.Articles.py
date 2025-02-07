import pandas as pd
import feedparser
import re
from collections import defaultdict
import os
import sys
from datetime import datetime

# Configure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

# Load the CSV file
project_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = "csvs\playersMvpTeamsGoogles.csv"
csv_path = os.path.join(project_directory, csv_file)
df = pd.read_csv(csv_path)

# Fetch ESPN NBA RSS feed
rss_url = "https://www.espn.com/espn/rss/nba/news"
feed = feedparser.parse(rss_url)

# List of players to check for first and last names
players_to_check = {
    "Giannis": "Giannis",
    "Luka": "Luka",
    "Kyrie": "Kyrie",
    "LeBron": "LeBron",
    "Shai": "Shai",
    "Kawhi": "Kawhi",
    "Bam": "Bam",
    "Chet": "Chet",
    "Kobe": "Kobe",
}

# Define a function to create regex pattern for each player
def create_pattern(player_name):
    name_parts = player_name.split()
    first_name = re.escape(name_parts[0])  # The first part is the first name
    last_name = re.escape(' '.join(name_parts[1:]))  # Everything after is the last name
    
    # Construct a regex that matches the full name, first name, and last name
    pattern = rf'\b({first_name}|{last_name}|{re.escape(player_name)})\b'
    return re.compile(pattern, re.IGNORECASE)

# Define a function to count mentions within a specific timeframe
def count_mentions_in_season(player_name, season, articles):
    year_start, year_end = season.split('-')
    start_date = datetime.strptime(f"{year_start}-10-01", "%Y-%m-%d")
    end_date = datetime.strptime(f"20{year_end}-06-30", "%Y-%m-%d")
    
    count_title = 0
    count_description = 0
    player_pattern = create_pattern(player_name)

    for entry in articles:
        # Parse the article's published date
        published_date = datetime(*entry.published_parsed[:6])
        
        # Check if the article's date falls within the season timeframe
        if start_date <= published_date <= end_date:
            # Check for mentions in the title
            title_text = entry.title
            count_title += len(player_pattern.findall(title_text))
            
            # Check for mentions in the description
            description_text = entry.description
            count_description += len(player_pattern.findall(description_text))
    
    return count_title, count_description

# Initialize a dictionary to count mentions
mention_counts = defaultdict(lambda: {'title': 0, 'description': 0})

# Count mentions for each player during their respective seasons
for index, row in df.iterrows():
    player_name = row['PLAYER']
    season = row['SEASON']
    title_mentions, description_mentions = count_mentions_in_season(player_name, season, feed.entries)
    mention_counts[(player_name, season)]['title'] = title_mentions
    mention_counts[(player_name, season)]['description'] = description_mentions

# Add the mention counts to the DataFrame
df['article_mentions_title'] = df.apply(lambda x: mention_counts[(x['PLAYER'], x['SEASON'])]['title'], axis=1)
df['article_mentions_description'] = df.apply(lambda x: mention_counts[(x['PLAYER'], x['SEASON'])]['description'], axis=1)

# Calculate total mentions and rank
df['total_article_mentions'] = df['article_mentions_title'] + df['article_mentions_description']
df['article_mentions_rank'] = df.groupby('SEASON')['total_article_mentions'].rank(ascending=False, method='dense')

# Save the updated DataFrame to a new CSV
output_file = 'playersMvpTeamsGooglesArticles.csv'
df.to_csv(output_file, index=False)
print(f"Data saved to '{output_file}' with {df.shape[0]} rows.")

# Output the counts for verification
#print(mention_counts)
