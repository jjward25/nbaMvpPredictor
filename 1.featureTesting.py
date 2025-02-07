import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_selection import RFE
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
import warnings

warnings.filterwarnings("ignore")

# Load the CSV file
project_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = "featureSets\csvs\/playersMvpTeamsGooglesArticles.csv"
csv_path = os.path.join(project_directory, csv_file)
df = pd.read_csv(csv_path)

# Filter out the 2024-25 season for training
df_train = df[df['SEASON'] != '2024-25']

# Select features and target variable
X = df_train.drop(columns=['MVP', 'SEASON', 'TEAM', 'PLAYER_ID', 'TEAM_ID', 'PLAYER'])
y = df_train['MVP']

# Using OneHotEncoder for categorical features
categorical_cols = X.select_dtypes(include=['object']).columns
encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
X_encoded = encoder.fit_transform(X[categorical_cols])
X = pd.concat([X.drop(categorical_cols, axis=1).reset_index(drop=True), pd.DataFrame(X_encoded)], axis=1)

# RFE Implementation
def perform_rfe(model, X_train, y_train, num_features_to_select):
    selector = RFE(model, n_features_to_select=num_features_to_select, step=1)
    selector = selector.fit(X_train, y_train)
    return selector.support_, selector.ranking_

# Initialize model for RFE
model = RandomForestClassifier(n_estimators=100, random_state=42)

# Specify how many features to select
num_features_to_select = 10  # Adjust based on your requirements

# Perform RFE to select important features
support, ranking = perform_rfe(model, X, y, num_features_to_select)  # Corrected function call here
selected_features = X.columns[support].tolist()

print("Selected Features from RFE:")
print(selected_features)
print("Feature Rankings from RFE:")
print(ranking)

# Correlation Matrix - Ensure only numeric columns
correlation_matrix = df_train.select_dtypes(include=['number']).corr()
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm')
plt.title("Correlation Matrix")
plt.show()

# Principal Component Analysis
pca = PCA(n_components=min(X.shape[0], X.shape[1]))  # Set to minimum of samples or features
X_pca = pca.fit_transform(X)

explained_variance = pca.explained_variance_ratio_
print("\nExplained Variance by Principal Components:")
for i, var in enumerate(explained_variance):
    print(f"Principal Component {i + 1}: {var:.4f}")

# Explanation of dimensions reduced in PCA
total_variance_explained = sum(explained_variance)
print(f"\nTotal variance explained by all phttp://localhost:3000/blog/articles/nbamvprincipal components: {total_variance_explained:.4f}")
print(f"Number of principal components used: {len(explained_variance)}")

plt.figure(figsize=(10, 6))
plt.plot(range(1, len(explained_variance) + 1), explained_variance, marker='o', linestyle='--')
plt.title('Scree Plot')
plt.xlabel('Principal Component')
plt.ylabel('Variance Explained')
plt.xticks(range(1, len(explained_variance) + 1))
plt.grid()
plt.show()

