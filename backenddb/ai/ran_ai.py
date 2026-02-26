def analyze_ran(df):
    """
    RAN – Fixation stability
    Measures horizontal gaze variance
    """
    if df.empty:
        return 0.0

    return float(df["x"].std())
