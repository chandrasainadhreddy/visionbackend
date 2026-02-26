import numpy as np
import pandas as pd


def extract_features_by_type(df, test_type):
    mean_x = df["x"].mean()
    std_x  = df["x"].std()
    mean_y = df["y"].mean()
    std_y  = df["y"].std()

    return [mean_x, std_x, mean_y, std_y]
