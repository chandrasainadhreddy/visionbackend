import numpy as np
import pandas as pd

def extract_vrg_features(df):
    if isinstance(df, str):
        df = pd.read_csv(df)

    if not {"lx", "rx"}.issubset(df.columns):
        raise ValueError("CSV missing lx/rx columns for VRG")

    disparity = np.abs(df["lx"].values - df["rx"].values)

    mean_disp = np.mean(disparity)
    std_disp = np.std(disparity)
    max_disp = np.max(disparity)

    return [mean_disp, std_disp, max_disp]
