import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

script_dir = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(script_dir, "..", "data", "dynamic_asl_dataset.csv")
MODEL_OUTPUT_PATH = os.path.join(script_dir, "..", "saved_models", "dynamic_asl_model.pkl")

#Only currently trains J,Z and 10 since those are the only ones I have captured so far
#in the future, for the phrases, make another collect_phrases_data.py along with its own train_phrases_model.py
#unless preferred to modify this file (and collect_dynamic_data) to accomodate dynamic letters, numbers, and phrases

def train_dynamic():
    if not os.path.exists(DATASET_PATH):
        print(f"❌ Error: Dataset not found at {DATASET_PATH}")
        return

    print("Loading Dynamic ASL Dataset...")
    df = pd.read_csv(DATASET_PATH)

    print(f"Total sequences loaded: {len(df)}")
    print("\nClass breakdown:")
    print(df['label'].value_counts())

    X = df.drop('label', axis=1).values
    y = df['label'].values

    # Train / Test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("\nTraining Dynamic Sequence Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print("\n" + "="*40)
    print(f"Dynamic Model Test Accuracy: {acc * 100:.2f}%")
    print("="*40)
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

    # Save model
    os.makedirs(os.path.dirname(MODEL_OUTPUT_PATH), exist_ok=True)
    joblib.dump(model, MODEL_OUTPUT_PATH)
    print(f"Dynamic model successfully saved to: {MODEL_OUTPUT_PATH}")


if __name__ == "__main__":
    train_dynamic()