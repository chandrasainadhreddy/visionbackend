def get_description(test_type, severity):
    messages = {
        "RAN": {
            "Normal": "Stable fixation detected.",
            "Mild Issue": "Minor fixation instability observed.",
            "Needs Attention": "Significant fixation instability."
        },
        "VRG": {
            "Normal": "Good binocular coordination.",
            "Mild Issue": "Slight vergence imbalance.",
            "Needs Attention": "Poor eye coordination detected."
        },
        "PUR": {
            "Normal": "Smooth eye movement observed.",
            "Mild Issue": "Minor pursuit irregularities.",
            "Needs Attention": "Poor smooth pursuit control."
        }
    }
    return messages[test_type][severity]
