
from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    mean_absolute_error,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


# Locate the BusWise project and dataset.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "data-generator" / "bus_data.csv"
MODEL_DIR = PROJECT_DIR / "model" / "saved_models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def main():
    print("Loading BusWise dataset...")

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_PATH}\n"
            "Check that bus_data.csv exists in data-generator."
        )

    data = pd.read_csv(DATA_PATH)

    required_columns = [
        "route_id",
        "day",
        "departure_hour",
        "weather",
        "traffic",
        "scheduled_minutes",
        "actual_minutes",
        "delay_minutes",
        "crowding",
    ]

    missing = set(required_columns) - set(data.columns)
    if missing:
        raise ValueError(f"Missing CSV columns: {sorted(missing)}")

    print(f"Dataset loaded: {len(data)} records")

    # Input features available before the journey.
    features = [
        "route_id",
        "day",
        "departure_hour",
        "weather",
        "traffic",
        "scheduled_minutes",
    ]

    # Remove rows with missing values in the fields we need.
    data = data.dropna(subset=features + ["delay_minutes", "crowding"])

    # Convert numeric columns safely.
    for column in [
        "departure_hour",
        "scheduled_minutes",
        "delay_minutes",
    ]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(
        subset=[
            "departure_hour",
            "scheduled_minutes",
            "delay_minutes",
        ]
    )

    X = data[features]
    y_delay = data["delay_minutes"].astype(float)
    y_crowding = data["crowding"].astype(str).str.strip().str.lower()

    print(f"Usable records: {len(data)}")
    print("Training delay prediction model...")

    # Keep the same rows in both tasks.
    X_train, X_test, y_delay_train, y_delay_test, y_crowd_train, y_crowd_test = (
        train_test_split(
            X,
            y_delay,
            y_crowding,
            test_size=0.2,
            random_state=42,
        )
    )

    categorical_features = ["route_id", "day", "weather", "traffic"]
    numeric_features = ["departure_hour", "scheduled_minutes"]

    def make_preprocessor():
        return ColumnTransformer(
            transformers=[
                (
                    "categorical",
                    OneHotEncoder(handle_unknown="ignore"),
                    categorical_features,
                ),
                ("numeric", "passthrough", numeric_features),
            ]
        )

    delay_model = Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=150,
                    random_state=42,
                    min_samples_leaf=2,
                    n_jobs=-1,
                ),
            ),
        ]
    )

    delay_model.fit(X_train, y_delay_train)
    delay_predictions = delay_model.predict(X_test)

    delay_mae = mean_absolute_error(y_delay_test, delay_predictions)

    print("\n--- Delay Model Results ---")
    print(f"Mean Absolute Error: {delay_mae:.2f} minutes")

    delay_model_path = MODEL_DIR / "delay_model.joblib"
    joblib.dump(delay_model, delay_model_path)
    print(f"Saved: {delay_model_path}")

    print("\nTraining crowding prediction model...")

    crowding_model = Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=150,
                    random_state=42,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    crowding_model.fit(X_train, y_crowd_train)
    crowd_predictions = crowding_model.predict(X_test)

    crowd_accuracy = accuracy_score(y_crowd_test, crowd_predictions)

    print("\n--- Crowding Model Results ---")
    print(f"Accuracy: {crowd_accuracy:.2%}")
    print("\nClassification report:")
    print(
        classification_report(
            y_crowd_test,
            crowd_predictions,
            zero_division=0,
        )
    )

    crowd_model_path = MODEL_DIR / "crowding_model.joblib"
    joblib.dump(crowding_model, crowd_model_path)
    print(f"Saved: {crowd_model_path}")

    print("\nBusWise model training completed!")
    print("Reminder: results use synthetic data, not real bus observations.")


if __name__ == "__main__":
    main()
