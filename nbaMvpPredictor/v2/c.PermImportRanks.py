import os
import sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_selection import VarianceThreshold
from eli5.sklearn import PermutationImportance
import eli5
import numpy as np

# Set default encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Load the players_with_mvp.csv file
absolute_path = os.path.dirname(__file__)
filename = 'playersRanks.csv'
file_path = os.path.join(absolute_path, filename)
players_df = pd.read_csv(file_path)

# Drop non-predictive columns, like player name and ID
players_df = players_df.drop(columns=['LEAGUE_ID','SEASON_ID','TEAM_ID','TEAM_ABBREVIATION','PLAYER_AGE','GP_y','GS','RANK_FGM','RANK_FGA','RANK_FG_PCT','RANK_FG3M','RANK_FG3A','RANK_FG3_PCT','RANK_FTM','RANK_FTA','RANK_FT_PCT','RANK_OREB','RANK_DREB'],errors='ignore')

# Separate features and target variable
X = players_df.drop(columns=['MVP'])
y = players_df['MVP']

# Drop rows with NaN values in X and y
X = X.dropna()
y = y[X.index]  # Ensure y is synchronized with X

# Convert categorical variables to dummy variables (if any)
X = pd.get_dummies(X, drop_first=True)

# Remove low-variance features
selector = VarianceThreshold(threshold=0.01)
X = selector.fit_transform(X)

# Use the feature names from the post-encoded DataFrame after applying VarianceThreshold
selected_columns = [col for col, keep in zip(pd.get_dummies(players_df.drop(columns=['MVP']), drop_first=True).columns, selector.get_support()) if keep]
X = pd.DataFrame(X, columns=selected_columns)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a weight array for the classes
weights = np.where(y_train == 1, 25, 1)  # 25 for MVPs, 1 for non-MVPs

# Initialize and fit RandomForest model with class weights
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train, sample_weight=weights)

# Compute permutation importance using eli5
perm = PermutationImportance(model, random_state=1).fit(X_test, y_test)

# Display the feature importance with eli5
print(eli5.format_as_text(eli5.explain_weights(perm, feature_names=X.columns.tolist())))

# (Optional) Create an ensemble model with VotingClassifier
# Example: Using RandomForest and another classifier, e.g., LogisticRegression
from sklearn.linear_model import LogisticRegression

# Initialize the second model
model2 = LogisticRegression(random_state=42, max_iter=1000)

# Create a voting classifier
voting_model = VotingClassifier(estimators=[
    ('rf', model), 
    ('lr', model2)
], voting='soft')  # or 'hard' depending on your needs

# Fit the ensemble model
voting_model.fit(X_train, y_train, sample_weight=weights)

# Optionally compute permutation importance for the ensemble model
perm_voting = PermutationImportance(voting_model, random_state=1).fit(X_test, y_test)
print(eli5.format_as_text(eli5.explain_weights(perm_voting, feature_names=X.columns.tolist())))
