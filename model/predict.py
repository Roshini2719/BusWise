
from pathlib import Path

import joblib
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = PROJECT_DIR / "model" / "saved_models"

delay_model = joblib.load(MODEL_DIR / "delay_model.joblib")
crowding_model = joblib.load(MODEL_DIR / "crowding_model.joblib")


def main():
    print("\n===== BusWise Prediction =====")

    route_id = input("Enter route ID (example: R01): ").strip()
    day = input("Enter day (Monday-Sunday): ").strip().capitalize()

    try:
        departure_hour = int(input("Departure hour (0-23): "))
        scheduled_minutes = float(input("Scheduled journey duration (minutes): "))
    except ValueError:
        print("Please enter valid numeric values.")
        return

    weather = input("Weather (Sunny/Rainy/Cloudy): ").strip().capitalize()
    traffic = input("Traffic (Low/Medium/High): ").strip().capitalize()

    if not 0 <= departure_hour <= 23:
        print("Departure hour must be between 0 and 23.")
        return

    if scheduled_minutes <= 0:
        print("Journey duration must be greater than zero.")
        return

    journey = pd.DataFrame([{
        "route_id": route_id,
        "day": day,
        "departure_hour": departure_hour,
        "weather": weather,
        "traffic": traffic,
        "scheduled_minutes": scheduled_minutes,
    }])

    predicted_delay = float(delay_model.predict(journey)[0])
    predicted_crowding = str(crowding_model.predict(journey)[0])

    # A negative delay means the model predicts an early arrival.
    print("\n===== Prediction Results =====")
    print(f"Route: {route_id}")
    print(f"Predicted delay: {predicted_delay:.1f} minutes")

    if predicted_delay > 0:
        print(f"Estimated journey duration: "
              f"{scheduled_minutes + predicted_delay:.1f} minutes")
    else:
        print("The model predicts the bus may arrive early.")

    print(f"Predicted crowding: {predicted_crowding.upper()}")
    print("\nNote: This prototype uses synthetic training data.")


if __name__ == "__main__":
    main()
