import tensorflow as tf
import numpy as np
import pandas as pd
import joblib
import requests  # Add this import

# Configuration - Add your web app URL here
WEB_APP_URL = "http://localhost:3000/api/model-output"

# Load model
model = tf.keras.models.load_model("rnn_lstm_letter_classifier.keras")

# Load scaler
scaler = joblib.load("scaler.pkl")
le = joblib.load("label_encoder.pkl")

# Load the file
df = pd.read_csv(r"C:\mrinank\COLLEGE\data_aquistion_pipeline\csv\data.csv")

# Keep only features you trained with
FEATURES = ["flex_1", "flex_2", "flex_3", "flex_4", "flex_5",
            "GYRx", "GYRy", "GYRz",
            "ACCx", "ACCy", "ACCz"]

df = df[FEATURES].dropna()

WINDOW, STEP = 120, 20

X_list = []
arr = df.values
for start in range(0, max(0, len(arr) - WINDOW + 1), STEP):
    end = start + WINDOW
    if end <= len(arr):
        X_list.append(arr[start:end])

X = np.stack(X_list)

X = scaler.transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)

pred_probs = model.predict(X)
pred_labels = pred_probs.argmax(axis=1)

decoded = le.inverse_transform(pred_labels)

print("Predicted letters:", decoded)

# ===== ADD THIS PART TO SEND TO WEB APP =====
# Combine letters into a string
predicted_text = ''.join(decoded)
print(f"Combined text: {predicted_text}")

# Send to web application
try:
    response = requests.post(WEB_APP_URL, json={'text': predicted_text}, timeout=5)
    response.raise_for_status()
    print(f"✓ Successfully sent to web app: {predicted_text}")
except requests.exceptions.RequestException as e:
    print(f"✗ Error sending to web app: {e}")
    print("Make sure your Next.js server is running on http://localhost:3000")
# ============================================


