import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
import requests
import time
from collections import deque

# Configuration
API_URL = "http://localhost:3000/api/model-output"  # Change if your server runs on different port
WINDOW_SIZE = 120
STEP_SIZE = 20

# Load model
print("Loading model...")
model = tf.keras.models.load_model("rnn_lstm_letter_classifier.keras")

# Load scaler and label encoder
print("Loading scaler and label encoder...")
scaler = joblib.load("scaler.pkl")
le = joblib.load("label_encoder.pkl")

def send_to_webapp(text):
    """Send predicted text to the web application."""
    try:
        response = requests.post(API_URL, json={'text': text}, timeout=2)
        response.raise_for_status()
        print(f"✓ Sent to web app: {text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"✗ Error sending to web app: {e}")
        return False

def process_csv_file(csv_path):
    """Process a CSV file and predict letters."""
    print(f"Loading data from: {csv_path}")
    df = pd.read_csv(csv_path)
    
    # Keep only features you trained with
    FEATURES = ["flex_1", "flex_2", "flex_3", "flex_4", "flex_5",
                "GYRx", "GYRy", "GYRz",
                "ACCx", "ACCy", "ACCz"]
    
    df = df[FEATURES].dropna()
    
    if len(df) < WINDOW_SIZE:
        print(f"Warning: Not enough data (need at least {WINDOW_SIZE} rows, got {len(df)})")
        return
    
    # Create windows
    X_list = []
    arr = df.values
    for start in range(0, max(0, len(arr) - WINDOW_SIZE + 1), STEP_SIZE):
        end = start + WINDOW_SIZE
        if end <= len(arr):
            X_list.append(arr[start:end])
    
    if not X_list:
        print("No valid windows created")
        return
    
    X = np.stack(X_list)
    
    # Scale the data
    X = scaler.transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
    
    # Predict
    print("Running predictions...")
    pred_probs = model.predict(X, verbose=0)
    pred_labels = pred_probs.argmax(axis=1)
    
    # Decode labels
    decoded = le.inverse_transform(pred_labels)
    
    # Combine letters into a string
    predicted_text = ''.join(decoded)
    
    print(f"Predicted letters: {decoded}")
    print(f"Combined text: {predicted_text}")
    
    # Send to web app
    send_to_webapp(predicted_text)
    
    return predicted_text

def process_realtime_data(df, buffer_size=5):
    """
    Process data in real-time with a buffer to reduce noise.
    
    Args:
        df: DataFrame with sensor data
        buffer_size: Number of recent predictions to buffer before sending
    """
    print(f"Processing real-time data...")
    
    FEATURES = ["flex_1", "flex_2", "flex_3", "flex_4", "flex_5",
                "GYRx", "GYRy", "GYRz",
                "ACCx", "ACCy", "ACCz"]
    
    df = df[FEATURES].dropna()
    
    if len(df) < WINDOW_SIZE:
        return
    
    # Get the most recent window
    arr = df.values[-WINDOW_SIZE:]
    X = arr.reshape(1, WINDOW_SIZE, len(FEATURES))
    
    # Scale
    X = scaler.transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)
    
    # Predict
    pred_probs = model.predict(X, verbose=0)
    pred_label = pred_probs.argmax(axis=1)[0]
    decoded_letter = le.inverse_transform([pred_label])[0]
    
    return decoded_letter

# Main execution
if __name__ == "__main__":
    # Process the CSV file
    csv_path = r"C:\mrinank\COLLEGE\data_aquistion_pipeline\csv\data.csv"
    
    try:
        predicted_text = process_csv_file(csv_path)
        print(f"\n✓ Processing complete!")
        print(f"Final output: {predicted_text}")
    except Exception as e:
        print(f"✗ Error during processing: {e}")
        import traceback
        traceback.print_exc()


