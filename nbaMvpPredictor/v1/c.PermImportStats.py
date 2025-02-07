import os, sys
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from eli5.sklearn import PermutationImportance
import eli5
import numpy as np

# Set default encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

# Load the players_with_mvp.csv file
absolute_path = os.path.dirname(__file__)
filename = 'players_with_mvp_googles.csv'
file_path = os.path.join(absolute_path, filename)
players_df = pd.read_csv(file_path)

# Drop non-predictive columns, like player name and ID
players_df = players_df.drop(columns=['PLAYER', 'PLAYER_ID','TEAM','RANK','SEASON'], errors='ignore')

# Separate features and target variable
X = players_df.drop(columns=['MVP'])
y = players_df['MVP']

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

# Initialize and fit RandomForest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Compute permutation importance using eli5
perm = PermutationImportance(model, random_state=1).fit(X_test, y_test)

# Display the feature importance with eli5
#eli5.show_weights(perm, feature_names=X.columns.tolist())
print(eli5.format_as_text(eli5.explain_weights(perm, feature_names=X.columns.tolist())))
