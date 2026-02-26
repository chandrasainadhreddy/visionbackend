from loaders.load_eye_data import load_eye_data
from ai.pur_ai import analyze_pur
from utils.severity import categorize
from utils.descriptions import get_description
from save.save_results import save_result

def run_pur(test_id):
    df = load_eye_data(test_id)
    score = analyze_pur(df)
    severity = categorize(score)
    description = get_description("PUR", severity)

    save_result(test_id, score, severity, description)

    return {
        "test_type": "Full Assessment",
        "score": score,
        "severity": severity,
        "description": description
    }
