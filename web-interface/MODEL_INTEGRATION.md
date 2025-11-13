# Model Integration Guide

This guide shows you how to connect your TensorFlow model to the web application.

## Quick Start

### 1. Install Required Packages

```bash
pip install requests
```

Or install all requirements:
```bash
pip install -r model_requirements.txt
```

### 2. Modify Your Model Code

You have two options:

#### Option A: Use the Modified Version (Recommended)

Use `model_original_modified.py` which is a direct modification of your original code with minimal changes.

**Key changes:**
- Added `import requests`
- Added code at the end to send predictions to the web app

#### Option B: Modify Your Existing Code

Add these lines to the end of your model script:

```python
import requests  # Add this at the top

# ... your existing code ...

# After printing decoded letters, add:
predicted_text = ''.join(decoded)

# Send to web application
try:
    response = requests.post(
        "http://localhost:3000/api/model-output", 
        json={'text': predicted_text}, 
        timeout=5
    )
    response.raise_for_status()
    print(f"✓ Successfully sent to web app: {predicted_text}")
except requests.exceptions.RequestException as e:
    print(f"✗ Error sending to web app: {e}")
```

### 3. Run Your Model

1. **Start the web application first:**
   ```bash
   cd sign-language-translator
   npm run dev
   ```
   The app should be running on `http://localhost:3000`

2. **Run your model:**
   ```bash
   python model_original_modified.py
   ```

3. **Watch the magic happen!**
   - Your model's output will automatically appear in the web app's input field
   - Translation will trigger automatically after 500ms
   - Speech will play automatically

## Real-Time Processing

If you want to process data continuously (e.g., from a live sensor stream), you can use the `process_realtime_data()` function in `model_inference.py`.

Example:
```python
# In a loop that receives new sensor data
while True:
    # Get new data (replace with your data acquisition method)
    new_data = get_sensor_data()  # Your function to get data
    
    # Process and get predicted letter
    letter = process_realtime_data(new_data)
    
    if letter:
        # Send individual letters or buffer them
        send_to_webapp(letter)
    
    time.sleep(0.1)  # Adjust based on your data rate
```

## Troubleshooting

### "Connection refused" error
- Make sure your Next.js server is running (`npm run dev`)
- Check that the server is on `http://localhost:3000`
- If using a different port, update `WEB_APP_URL` in your model code

### Predictions not appearing in web app
- Check browser console for errors
- Verify the API endpoint is accessible: `http://localhost:3000/api/model-output`
- Make sure the web page is open and connected

### Multiple letters being sent too quickly
- The web app has a 500ms debounce, so rapid updates will be batched
- If needed, you can buffer letters in your model code before sending

## API Details

**Endpoint:** `POST /api/model-output`

**Request Body:**
```json
{
  "text": "Your predicted text here"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Output received and broadcasted"
}
```

## Example Output Flow

1. Model predicts: `['H', 'E', 'L', 'L', 'O']`
2. Combines to: `"HELLO"`
3. Sends to web app via API
4. Web app receives and displays in input field
5. Auto-translation triggers after 500ms
6. Translated text appears and speech plays


