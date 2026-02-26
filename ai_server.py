from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd
import numpy as np
import joblib
import os
import sys
import traceback

# Import local feature extraction (supports DataFrames)
try:
    from feature_extraction import extract_ran_features, extract_vrg_features, extract_pur_features
    print("✅ Local feature extraction modules loaded")
except ImportError as e:
    print(f"❌ Error loading feature_extraction.py: {e}")
    sys.exit(1)

app = Flask(__name__)

# =========================
# DATABASE CONFIG
# =========================
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'binoculardb'
}

# =========================
# MODELS PATH
# =========================
# 1. Local Models folder
LOCAL_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Models")
# 2. User provided path (Fallback)
USER_MODELS_DIR = r"C:\Users\VAMSI BOGGULA\gazebasevr_project\Models"

models = {}
scalers = {}

def load_models():
    """Load models from available directories"""
    search_paths = [LOCAL_MODELS_DIR, USER_MODELS_DIR]
    
    for test_type in ['ran', 'vrg', 'pur']:
        loaded = False
        for models_dir in search_paths:
            if not os.path.exists(models_dir):
                continue
                
            model_path = os.path.join(models_dir, f"model_{test_type}.pkl")
            scaler_path = os.path.join(models_dir, f"scaler_{test_type}.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                try:
                    models[test_type] = joblib.load(model_path)
                    scalers[test_type] = joblib.load(scaler_path)
                    print(f"✅ Loaded {test_type.upper()} model from: {models_dir}")
                    loaded = True
                    break
                except Exception as e:
                    print(f"⚠️ Error loading {test_type} from {models_dir}: {e}")
        
        if not loaded:
            print(f"⚠️ {test_type.upper()} model not found in any search path.")

# Load models on startup
load_models()

# =========================
# VALIDATION UTILS
# =========================
def validate_metrics(metrics):
    """Ensure all metrics are infinite/valid floats"""
    clean = {}
    for k, v in metrics.items():
        try:
            val = float(v)
            if np.isfinite(val):
                clean[k] = val
            else:
                clean[k] = 0.0
        except:
            clean[k] = 0.0
    return clean

# =========================
# HELPER FUNCTIONS
# =========================
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_eye_data(test_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT n, x, y, lx, ly, rx, ry
            FROM eye_data
            WHERE test_id = %s
            ORDER BY n ASC
        """
        cursor.execute(query, (test_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows: return None
        return pd.DataFrame(rows)
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def analyze_with_model(df, test_type):
    try:
        tt = test_type.lower()
        if tt not in models or tt not in scalers:
            return None
            
        model = models[tt]
        scaler = scalers[tt]
        
        metrics = {}
        feats = []
        
        # Feature Extraction
        if tt == 'ran':
            # returns [mean, std, max, ratio]
            feats = extract_ran_features(df)
            metrics = {
                "mean_speed": feats[0],
                "std_speed": feats[1],
                "max_speed": feats[2],
                "fixation_ratio": feats[3]
            }
            
        elif tt == 'vrg':
            # returns [mean, std, max]
            feats = extract_vrg_features(df)
            metrics = {
                "mean_disparity": feats[0],
                "std_disparity": feats[1],
                "max_disparity": feats[2]
            }
            
        elif tt == 'pur':
            # returns [mean, std, max]
            feats = extract_pur_features(df)
            metrics = {
                "mean_speed": feats[0],
                "std_speed": feats[1],
                "max_speed": feats[2]
            }
        else:
            return None

        # Scale using numpy array to avoid column name mismatch
        Xs = scaler.transform(np.array([feats]))
        
        # Predict
        if hasattr(model, "decision_function"):
            raw_score = float(model.decision_function(Xs)[0])
            score = raw_score # User script logic: Raw score with thresholds
        else:
            # Fallback if model is not SVM-like
            score = float(model.predict(Xs)[0])

        # Classification (User's Logic)
        if score > 0.6:
            classification = "Normal"
        elif score > 0.3:
            classification = "Mild Issue"
        else:
            classification = "Needs Attention"
            
        return {
            "score": round(score, 4),
            "classification": classification,
            "metrics": validate_metrics(metrics)
        }
        
    except Exception as e:
        print(f"Model analysis failed: {e}")
        traceback.print_exc()
        return None

def rule_based_analysis(df, test_type):
    """Fallback logic if ML fails"""
    try:
        # Simple calculations for fallback
        if 'x' not in df.columns:
            df['x'] = (df['lx'] + df['rx']) / 2
            df['y'] = (df['ly'] + df['ry']) / 2
            
        dx = np.diff(df["x"].values)
        dy = np.diff(df["y"].values)
        speed = np.sqrt(dx**2 + dy**2)
        
        metrics = {}
        score = 0.5
        
        tt = test_type.upper()
        if tt == "RAN":
            fr = np.mean(speed < 5.0) if len(speed) > 0 else 0
            metrics = {"mean_speed": np.mean(speed), "fixation_ratio": fr}
            score = fr # Rough approximation
        elif tt == "VRG":
            disp = np.abs(df["lx"] - df["rx"])
            metrics = {"mean_disparity": np.mean(disp)}
            score = 1.0 / (1.0 + np.std(disp))
        elif tt == "PUR":
            metrics = {"mean_speed": np.mean(speed)}
            score = 1.0 / (1.0 + np.std(speed))
            
        classification = "Mild Issue"
        if score > 0.7: classification = "Normal"
        elif score < 0.3: classification = "Needs Attention"
        
        return {
            "score": round(score, 4),
            "classification": classification,
            "metrics": validate_metrics(metrics)
        }
    except Exception as e:
        print(f"Rule-based failed: {e}")
        return {"score": 0, "classification": "Error", "metrics": {}}

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        test_id = data.get("test_id")
        test_type = data.get("test_type")
        
        if not test_id or not test_type:
            return jsonify({"error": "Missing params"}), 400
            
        print(f"Analyze request: ID={test_id} Type={test_type}")
        
        df = fetch_eye_data(test_id)
        if df is None or len(df) < 10:
            return jsonify({"error": "Insufficient data"}), 400
            
        result = analyze_with_model(df, test_type)
        if result is None:
            print("Fallback to rule-based")
            result = rule_based_analysis(df, test_type)
            
        return jsonify({
            "status": True,
            "classification": result["classification"],
            "score": result["score"],
            "metrics": result.get("metrics", {}),
            "notes": f"Analysis for Test #{test_id}"
        })
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running", 
        "models": {k: "loaded" for k in models}
    })

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
