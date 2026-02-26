import os
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

# PATHS
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "Datasets")
MODEL_DIR = os.path.join(BASE_DIR, "Models")

os.makedirs(MODEL_DIR, exist_ok=True)

def extract_features_from_csv(df):
    mean_x = df["x"].mean()
    std_x  = df["x"].std()
    mean_y = df["y"].mean()
    std_y  = df["y"].std()
    return [mean_x, std_x, mean_y, std_y]

def train_for_test(test_type):
    print(f"\nTraining model for {test_type.upper()}")

    file_path = os.path.join(DATA_DIR, f"{test_type}.csv")

    if not os.path.exists(file_path):
        print("Dataset not found:", file_path)
        return

    df = pd.read_csv(file_path)

    window_size = 20
    features_list = []

    for i in range(0, len(df) - window_size, window_size):
        window = df.iloc[i:i+window_size]
        features = extract_features_from_csv(window)
        features_list.append(features)

    X = np.array(features_list)

    print("Feature shape:", X.shape)

    if len(X) < 5:
        print("❌ Not enough samples")
        return

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = IsolationForest(
        n_estimators=200,
        contamination=0.1,
        random_state=42
    )

    model.fit(X_scaled)

    joblib.dump(model, os.path.join(MODEL_DIR, f"model_{test_type}.pkl"))
    joblib.dump(scaler, os.path.join(MODEL_DIR, f"scaler_{test_type}.pkl"))

    print(f"✅ Saved model_{test_type}.pkl")

if __name__ == "__main__":
    for t in ["ran", "pur", "vrg"]:
        train_for_test(t)

    print("\n🔥 Training completed.")
