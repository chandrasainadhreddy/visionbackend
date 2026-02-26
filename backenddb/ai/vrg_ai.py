def analyze_vrg(df):
    """
    VRG – Vergence (Quick Screening)
    Measures average disparity between left and right eye
    """
    if df.empty:
        return 0.0

    disparity = (df["lx"] - df["rx"]).abs()
    return float(disparity.mean())
