import numpy as np
import pandas as pd

def extract_pur_features(df):
    if isinstance(df, str):
        df = pd.read_csv(df)

    if not {"x", "y", "n"}.issubset(df.columns):
        raise ValueError("CSV missing required columns for PUR")

    t = df["n"].values / 1000.0
    x = df["x"].values
    y = df["y"].values

    dx = np.diff(x)
    dy = np.diff(y)
    dt = np.diff(t)
    dt[dt == 0] = 1e-6

    velocity = np.sqrt(dx**2 + dy**2) / dt

    return [
        np.mean(velocity),
        np.std(velocity),
        np.max(velocity)
    ]
