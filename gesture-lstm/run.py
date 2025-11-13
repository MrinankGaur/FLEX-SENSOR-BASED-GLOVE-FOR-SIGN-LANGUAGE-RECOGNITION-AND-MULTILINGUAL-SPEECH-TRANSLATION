import os
import time
import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
import requests

# ===================== CONFIG =====================
# Update this path to match your system (Windows or Linux)
# For Windows: Use "C:\\path\\to\\folder" or r"C:\path\to\folder"
# For Linux: Use "/home/user/path/to/folder"
WATCH_DIR = "C:\\mrinank\\COLLEGE\\PROJECT 1\\DATA_AQUISITION"  # Folder to watch
TARGET_FILE = "data.csv"      # Editable filename (original file will NOT be deleted)
CHECK_INTERVAL = 3            # Seconds between checks (increased from 2 to reduce frequency)
API_ENDPOINT = "http://localhost:3000/api/model-output"  # Translator API endpoint

# ===================== MODEL & SCALER =====================
model = tf.keras.models.load_model("rnn_lstm_letter_classifier.keras")
scaler = joblib.load("scaler.pkl")
le = joblib.load("label_encoder.pkl")

FEATURES = [
    "flex_1", "flex_2", "flex_3", "flex_4", "flex_5",
    "GYRx", "GYRy", "GYRz",
    "ACCx", "ACCy", "ACCz"
]

WINDOW, STEP = 120, 20


# ===================== PROCESSING FUNCTION =====================
def process_file(file_path):
    print(f"\n📄 Processing: {file_path}")
    
    try:
        # Read directly from the original file - NO copies created
        # Data is loaded into memory only
        df = pd.read_csv(file_path)
        df = df[FEATURES].dropna()

        arr = df.values
        X_list = []

        for start in range(0, max(0, len(arr) - WINDOW + 1), STEP):
            end = start + WINDOW
            if end <= len(arr):
                X_list.append(arr[start:end])

        if not X_list:
            print("⚠️ No valid data windows found. Skipping file.")
            return

        X = np.stack(X_list)
        X = scaler.transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)

        pred_probs = model.predict(X)
        pred_labels = pred_probs.argmax(axis=1)
        decoded = le.inverse_transform(pred_labels)

        # Combine predicted letters into a single string
        predicted_text = ''.join(decoded)

        print("✅ Predicted letters:", decoded)
        print("✅ Predicted text:", predicted_text)

        # ========== Send to Translator API ==========
        try:
            response = requests.post(API_ENDPOINT, 
                                    json={'text': predicted_text})
            response.raise_for_status()  # Raises an error for bad status codes
            print(f"🌐 Successfully sent to translator API. Response: {response.json()}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending to translator API: {e}")
        
        print(f"✅ Processing complete. Original file untouched: {file_path}\n")
    
    except Exception as e:
        print(f"❌ Error during processing: {e}\n")


# ===================== WATCH LOOP =====================
print(f"👀 Watching directory: {WATCH_DIR}")
print(f"Waiting for file: {TARGET_FILE}")

while True:
    target_path = os.path.join(WATCH_DIR, TARGET_FILE)

    if os.path.exists(target_path):
        try:
            process_file(target_path)
        except Exception as e:
            print(f"❌ Error while processing: {e}")
        time.sleep(CHECK_INTERVAL)  # Wait before checking again after processing
    else:
        time.sleep(CHECK_INTERVAL)
