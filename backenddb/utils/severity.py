def categorize(score):
    if score < 0.05:
        return "Normal"
    elif score < 0.15:
        return "Mild Issue"
    else:
        return "Needs Attention"
