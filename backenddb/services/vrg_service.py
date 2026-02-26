from loaders.load_eye_data import load_eye_data
from ai.vrg_ai import analyze_vrg
from utils.severity import categorize
from utils.descriptions import get_description
from save.save_results import save_result

def run_vrg(test_id):
    df = load_eye_data(test_id)
    score = analyze_vrg(df)
    severity = categorize(score)
    description = get_description("VRG", severity)

    save_result(test_id, score, severity, description)

    return {
        "test_type": "Quick Screening",
        "score": score,
        "severity": severity,
        "description": description
    }
