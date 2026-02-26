def analyze_pur(df):
    """
    PUR – Smooth pursuit
    Measures frame-to-frame gaze change
    """
    if df.empty:
        return 0.0

    return float(df["x"].diff().abs().mean())
