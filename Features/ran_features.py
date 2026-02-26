import pandas as pd
import numpy as np

def extract_ran_features(csv_file):
    """
    Extract RAN (Fixation + Saccades) features from CSV
    Expected columns: n (ms), x, y
    """

    df = pd.read_csv(csv_file)

    required_cols = {"n", "x", "y"}
    if not required_cols.issubset(df.columns):
        raise ValueError("CSV missing required columns for RAN")

    # Time in seconds
    t = df["n"].values / 1000.0
    x = df["x"].values
    y = df["y"].values

    # Differences
    dx = np.diff(x)
    dy = np.diff(y)
    dt = np.diff(t)

    # Avoid divide-by-zero
    dt[dt == 0] = 1e-6

    velocity = np.sqrt(dx**2 + dy**2) / dt

    mean_vel = np.mean(velocity)
    std_vel = np.std(velocity)
    max_vel = np.max(velocity)

    # Fixation ratio (velocity threshold)
    fixation_ratio = np.sum(velocity < 5.0) / len(velocity)

    return [mean_vel, std_vel, max_vel, fixation_ratio]
