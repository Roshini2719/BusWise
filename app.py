
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "model" / "saved_models"
DATA_PATH = BASE_DIR / "data-generator" / "bus_data.csv"

app = Flask(__name__)

# Load trained models once when the server starts.
delay_model = joblib.load(MODEL_DIR / "delay_model.joblib")
crowding_model = joblib.load(MODEL_DIR / "crowding_model.joblib")

# Populate the route dropdown from the generated dataset.
data = pd.read_csv(DATA_PATH)
route_ids = sorted(data["route_id"].dropna().astype(str).unique())

FEATURES = [
    "route_id",
    "day",
    "departure_hour",
    "weather",
    "traffic",
    "scheduled_minutes",
]


@app.route("/")
def home():
    return render_template("index.html", route_ids=route_ids)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        values = request.get_json(silent=True) or {}

        route_id = str(values.get("route_id", "")).strip()
        day = str(values.get("day", "")).strip().capitalize()
        weather = str(values.get("weather", "")).strip().capitalize()
        traffic = str(values.get("traffic", "")).strip().capitalize()

        if route_id not in route_ids:
            return jsonify({"error": "Please select a valid route."}), 400

        if day not in [
            "Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday"
        ]:
            return jsonify({"error": "Please select a valid day."}), 400

        if weather not in ["Sunny", "Rainy", "Cloudy"]:
            return jsonify({"error": "Please select valid weather."}), 400

        if traffic not in ["Low", "Medium", "High"]:
            return jsonify({"error": "Please select valid traffic."}), 400

        try:
            hour = int(values.get("departure_hour"))
            duration = float(values.get("scheduled_minutes"))
        except (TypeError, ValueError):
            return jsonify({
                "error": "Enter a valid departure hour and journey duration."
            }), 400

        if not 0 <= hour <= 23:
            return jsonify({"error": "Hour must be between 0 and 23."}), 400

        if not 1 <= duration <= 600:
            return jsonify({
                "error": "Journey duration must be between 1 and 600 minutes."
            }), 400

        journey = pd.DataFrame([{
            "route_id": route_id,
            "day": day,
            "departure_hour": hour,
            "weather": weather,
            "traffic": traffic,
            "scheduled_minutes": duration,
        }], columns=FEATURES)

        delay = float(delay_model.predict(journey)[0])
        crowding = str(crowding_model.predict(journey)[0]).upper()

        return jsonify({
            "route_id": route_id,
            "delay_minutes": round(delay, 1),
            "scheduled_minutes": round(duration, 1),
            "estimated_duration": round(duration + delay, 1),
            "crowding": crowding,
            "notice": (
                "Prototype prediction based on synthetic data. "
                "Not a live bus estimate."
            ),
        })

    except Exception:
        app.logger.exception("Prediction failed")
        return jsonify({
            "error": "Prediction failed. Check the server terminal for details."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
