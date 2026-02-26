from loaders.load_eye_data import load_eye_data
from ai.ran_ai import analyze_ran
from utils.severity import categorize
from utils.descriptions import get_description
from save.save_results import save_result

def run_ran(test_id):
    df = load_eye_data(test_id)
    score = analyze_ran(df)
    severity = categorize(score)
    description = get_description("RAN", severity)

    save_result(test_id, score, severity, description)

    return {
        "test_type": "Fixation Test",
        "score": score,
        "severity": severity,
        "description": description
    }
