# Sign Language Translation System

A comprehensive smart glove-based sign language translation system that captures hand gestures, converts them to text using machine learning, and provides real-time translation and text-to-speech capabilities in multiple languages.

## 🎯 Project Overview

This project consists of three main components working together to create an end-to-end sign language translation system:

1. **Data Acquisition Module** - Collects sensor data from a smart glove via serial communication
2. **Machine Learning Model** - LSTM/RNN-based gesture classifier that converts sensor data to letters
3. **Web Interface** - Next.js application for real-time translation and text-to-speech in multiple languages

## 📁 Project Structure

```
PROJECT 1/
├── DATA_AQUISITION/          # Data collection from smart glove
│   ├── csv_generator.py      # Serial data logger and CSV generator
│   └── data.csv              # Generated sensor data files
│
├── gesture-lstm/            # Machine learning model
│   ├── run.py                # Model inference script with file watcher
│   ├── rnn_lstm_letter_classifier.keras  # Trained model
│   ├── scaler.pkl            # Data preprocessing scaler
│   ├── label_encoder.pkl     # Label encoder for predictions
│   ├── requirements.txt      # Python dependencies
│   ├── setup.bat             # Windows setup script
│   ├── setup.sh              # Linux/macOS setup script
│   └── venv/                 # Virtual environment
│
└── web-interface/           # Next.js web application
    ├── app/                  # Next.js app directory
    │   ├── api/              # API routes
    │   │   ├── model-output/ # Server-Sent Events endpoint
    │   │   ├── translate/    # Translation API
    │   │   └── tts/          # Text-to-speech API
    │   ├── components/       # React components
    │   │   ├── Translator.tsx # Main translation component
    │   │   └── Navbar.tsx    # Navigation component
    │   └── page.tsx          # Home page
    ├── model_inference.py    # Model integration helper
    ├── MODEL_INTEGRATION.md  # Integration guide
    ├── package.json          # Node.js dependencies
    └── gcloud-credentials.json # Google Cloud credentials
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Node.js 18+** with npm
- **Serial port access** (for data acquisition)
- **Google Cloud account** with Text-to-Speech and Translation APIs enabled
- **Smart glove hardware** with:
  - 5 flex sensors
  - 3-axis gyroscope (GYR)
  - 3-axis accelerometer (ACC)
  - ESP32 or compatible microcontroller

### Installation

#### 1. Setup Machine Learning Environment

**Windows:**
```bash
cd gesture-lstm
setup.bat
```

**Linux/macOS:**
```bash
cd gesture-lstm
chmod +x setup.sh
./setup.sh
```

This will create a virtual environment and install all required Python packages.

#### 2. Setup Web Interface

```bash
cd web-interface
npm install
```

#### 3. Configure Google Cloud Credentials

1. Create a Google Cloud project and enable:
   - Cloud Translation API
   - Cloud Text-to-Speech API
2. Download service account credentials JSON
3. Place it in `web-interface/gcloud-credentials.json`

## 🔧 Configuration

### Data Acquisition (`DATA_AQUISITION/csv_generator.py`)

Update these variables in `csv_generator.py`:

```python
SERIAL_PORT = 'COM6'        # Change to your serial port
BAUD_RATE = 115200          # Match your device baud rate
OUTPUT_DIR = "..."          # Update to your project path
LINES_PER_FILE = 120        # Number of data points per CSV file
```

### Model Inference (`gesture-lstm/run.py`)

Update these variables in `run.py`:

```python
WATCH_DIR = "C:\\mrinank\\COLLEGE\\PROJECT 1\\DATA_AQUISITION"  # Data directory
TARGET_FILE = "data.csv"    # File to watch
API_ENDPOINT = "http://localhost:3000/api/model-output"  # Web app endpoint
```

## 📖 Usage

### Step 1: Start the Web Interface

```bash
cd web-interface
npm run dev
```

The application will be available at `http://localhost:3000`

### Step 2: Activate ML Environment and Run Model

**Windows:**
```bash
cd gesture-lstm
call venv\Scripts\activate.bat
python run.py
```

**Linux/macOS:**
```bash
cd gesture-lstm
source venv/bin/activate
python run.py
```

The model will watch the data directory for new CSV files and process them automatically.

### Step 3: Collect Data from Smart Glove

```bash
cd DATA_AQUISITION
python csv_generator.py
```

This script will:
- Connect to the smart glove via serial port
- Collect sensor data (flex sensors, gyroscope, accelerometer)
- Filter out resting hand positions
- Save data to `data.csv` when buffer is full (120 data points)

### Data Flow

1. **Smart Glove** → Serial communication → `csv_generator.py`
2. **CSV File** → File watcher → `run.py` (model inference)
3. **Model Output** → HTTP POST → Web interface API
4. **Web Interface** → Server-Sent Events → Real-time display
5. **Translation** → Google Cloud Translation API
6. **Speech** → Google Cloud Text-to-Speech API

## 🎨 Features

### Web Interface

- **Real-time Gesture Recognition**: Receives model predictions via Server-Sent Events
- **Multi-language Translation**: Supports 6 languages:
  - English (en-US)
  - Hindi (hi-IN)
  - Tamil (ta-IN)
  - Malayalam (ml-IN)
  - Telugu (te-IN)
  - Kannada (kn-IN)
- **Text-to-Speech**: Converts translated text to natural speech
- **Voice Gender Selection**: Choose between male and female voices
- **Auto-translation**: Automatically translates when new gestures are detected
- **Modern UI**: Built with Next.js, React, and Tailwind CSS

### Machine Learning Model

- **LSTM/RNN Architecture**: Deep learning model for sequence classification
- **11 Input Features**:
  - 5 flex sensor values
  - 3 gyroscope axes (X, Y, Z)
  - 3 accelerometer axes (X, Y, Z)
- **Sliding Window Processing**: 120 data points per window with 20-point step
- **Real-time Inference**: Processes new data files automatically

### Data Acquisition

- **Serial Communication**: Connects to ESP32/Arduino devices
- **Data Filtering**: Automatically filters resting hand positions
- **CSV Export**: Structured data format for model training/inference
- **Error Handling**: Robust error handling for serial communication issues

## 🔬 Technical Details

### Sensor Data Format

Each data point contains 11 values:
```
flex_1, flex_2, flex_3, flex_4, flex_5,
GYRx, GYRy, GYRz,
ACCx, ACCy, ACCz
```

### Model Architecture

- **Type**: LSTM/RNN neural network
- **Input Shape**: (120, 11) - 120 timesteps × 11 features
- **Output**: Letter classification (A-Z)
- **Preprocessing**: StandardScaler normalization

### API Endpoints

#### POST `/api/model-output`
Receives model predictions from the ML script.

**Request:**
```json
{
  "text": "HELLO"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Output received and broadcasted"
}
```

#### GET `/api/model-output`
Server-Sent Events endpoint for real-time updates to the frontend.

#### POST `/api/translate`
Translates text to target language.

**Request:**
```json
{
  "text": "HELLO",
  "targetLanguage": "hi"
}
```

#### POST `/api/tts`
Generates speech audio from text.

**Request:**
```json
{
  "text": "नमस्ते",
  "languageCode": "hi-IN",
  "gender": "FEMALE"
}
```

## 🛠️ Development

### Adding New Languages

1. Add language option to `languageOptions` in `Translator.tsx`
2. Ensure Google Cloud Translation API supports the language
3. Add corresponding Text-to-Speech voice code

### Training New Models

1. Collect training data using `csv_generator.py`
2. Label data with corresponding letters
3. Train model using TensorFlow/Keras
4. Save model as `.keras` file
5. Update `run.py` to load new model

### Customizing Data Collection

Modify `csv_generator.py`:
- Change `LINES_PER_FILE` for different buffer sizes
- Adjust filtering logic for resting position detection
- Add additional sensors by extending `COLUMN_NAMES`

## 📝 Dependencies

### Python (gesture-lstm)
- tensorflow
- scikit-learn
- numpy
- pandas
- joblib
- requests

### Node.js (web-interface)
- next
- react
- @google-cloud/text-to-speech
- @google-cloud/translate
- tailwindcss
- typescript

## 🐛 Troubleshooting

### Serial Port Issues
- **Error**: "Could not open port"
  - Check if port name is correct (COM6, /dev/ttyUSB0, etc.)
  - Ensure no other program is using the port
  - Verify device is connected and drivers are installed

### Model Not Processing Files
- Ensure `WATCH_DIR` path is correct in `run.py`
- Check that CSV files are being created in the watched directory
- Verify model files (`rnn_lstm_letter_classifier.keras`, `scaler.pkl`, `label_encoder.pkl`) exist

### Web Interface Not Receiving Data
- Verify Next.js server is running on `http://localhost:3000`
- Check API endpoint URL in `run.py` matches server address
- Ensure browser console shows no connection errors
- Verify Server-Sent Events connection is established

### Translation/Speech Errors
- Verify Google Cloud credentials file exists and is valid
- Check that APIs are enabled in Google Cloud Console
- Ensure billing is enabled for your Google Cloud project
- Check API quotas haven't been exceeded

## 📄 License

This project is developed for educational purposes.

## 👥 Contributors

Project developed for college coursework.

## 🙏 Acknowledgments

- TensorFlow/Keras for machine learning framework
- Next.js for web framework
- Google Cloud for translation and TTS services
- ESP32 community for hardware support

---

For detailed integration instructions, see `web-interface/MODEL_INTEGRATION.md`

