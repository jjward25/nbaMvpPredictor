import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import OneHotEncoder

import warnings
warnings.filterwarnings("ignore")

# Load the CSV file
project_directory = os.path.dirname(os.path.abspath(__file__))
csv_file = "featureSets\csvs\playersMvpTeamsGooglesArticles.csv"
csv_path = os.path.join(project_directory, csv_file)
df = pd.read_csv(csv_path)

# Filter out the 2024-25 season for training
df_train = df[df['SEASON'] != '2024-25']
df_test = df[df['SEASON'] == '2024-25']

# Select features and target variable
features = ['MIN_per_game', 'EFF_per_game', 'PTS_per_game_rank', 'PTS_rank', 'EFF_rank', 'WIN_PCT']
X = df_train[features]  # Use the specific features you want for training
y = df_train['MVP']

# Identify categorical columns (if any) in the training features
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

# Using OneHotEncoder for categorical features if they exist
encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)

# If there are categorical columns, fit and transform them
if categorical_cols:
    X_encoded = encoder.fit_transform(X[categorical_cols])
    X = pd.concat([X.drop(categorical_cols, axis=1).reset_index(drop=True), pd.DataFrame(X_encoded)], axis=1)

# Before splitting into train and validation sets
smote = SMOTE(random_state=42)

# Fit SMOTE to the training data
X_train_resampled, y_train_resampled = smote.fit_resample(X, y)

# Now, split the resampled data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X_train_resampled, y_train_resampled, test_size=0.2, random_state=42)

# Initialize the models
models = {
    "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingClassifier(n_estimators=100, random_state=42),
    "XGBoost": XGBClassifier(n_estimators=100, use_label_encoder=False, eval_metric='logloss', random_state=42)
}

# Train each model and evaluate performance
results = {}
for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    f1 = f1_score(y_val, y_pred)
    results[model_name] = {'accuracy': accuracy, 'f1_score': f1}
    print(f"{model_name} Accuracy: {accuracy:.3f}, F1 Score: {f1:.3f}")

# Prepare X_test_final using the same features for prediction
X_test_final = df_test[features]  # Use the same features as in training

# Apply the same OneHotEncoder for the test dataset
if categorical_cols:
    X_test_encoded = encoder.transform(X_test_final[categorical_cols])
    X_test_final = pd.concat([X_test_final.drop(categorical_cols, axis=1).reset_index(drop=True), pd.DataFrame(X_test_encoded)], axis=1)

# Now, predict the 2024-25 MVP with each model
predictions = {}
print("\nMVP Predictions for 2024-25 Season:")
for model_name, model in models.items():
    pred = model.predict(X_test_final)
    df_test[f'{model_name}_MVP_Prediction'] = pred
    predictions[model_name] = pred
    print(f"{model_name} Predicted MVP: {df_test[df_test[f'{model_name}_MVP_Prediction'] == 1]['PLAYER'].values}")
