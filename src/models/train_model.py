import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib


def train_model(csv_path):
    print("1. Loading dataset...")
    df = pd.read_csv(csv_path)

    # 2. Separate features (X) and target labels (y)
    X = df.drop(columns=['label'])
    y = df['label']

    # 3. Encode text labels to numerical indices
    print("2. Encoding labels...")
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    # 4. Split into Train (80%) and Test (20%) sets
    print("3. Splitting data into train/test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    # 5. Initialize and train the model
    print("4. Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 6. Evaluate accuracy
    print("5. Evaluating performance...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n🎉 Test Set Accuracy: {accuracy * 100:.2f}%\n")

    # Detailed report showing precision/recall per sign
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    # 7. Save model and label encoder for live webcam inference
    joblib.dump(model, 'asl_model.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')
    print("✅ Model saved to 'asl_model.pkl'")
    print("✅ Label Encoder saved to 'label_encoder.pkl'")

if __name__ == "__main__":
    train_model("extracted_asl_data.csv")
