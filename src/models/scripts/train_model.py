import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
import joblib


def train_model(csv_path, output_dir):
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

    print("Classification Report:")
    print(
        classification_report(
            y_test, 
            y_pred, 
            labels=range(len(label_encoder.classes_)), 
            target_names=label_encoder.classes_
        )
    )

    # 7. Save model and label encoder to saved_models/
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'asl_model.pkl')
    encoder_path = os.path.join(output_dir, 'label_encoder.pkl')

    joblib.dump(model, model_path)
    joblib.dump(label_encoder, encoder_path)
    print(f"✅ Model saved to '{model_path}'")
    print(f"✅ Label Encoder saved to '{encoder_path}'")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file_path = os.path.join(script_dir, "..", "data", "extracted_real_asl_data.csv")
    output_directory = os.path.join(script_dir, "..", "saved_models")

    train_model(csv_file_path, output_directory)