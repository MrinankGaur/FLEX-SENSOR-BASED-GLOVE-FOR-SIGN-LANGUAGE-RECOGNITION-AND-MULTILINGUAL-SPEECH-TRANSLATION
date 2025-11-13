#!/bin/bash
set -e # stop on error

# ---- CONFIG ----
VENV_DIR="venv"
PYTHON_BIN="python3"

echo "🔧 Setting up Python environment..."

# Step 1: Check if Python exists
if ! command -v $PYTHON_BIN &>/dev/null; then
  echo "❌ Python not found. Please install Python 3 first."
  exit 1
fi

# Step 2: Create virtual environment if not exists
if [ ! -d "$VENV_DIR" ]; then
  echo "🛠️ Creating virtual environment..."
  $PYTHON_BIN -m venv $VENV_DIR
else
  echo "✅ Virtual environment already exists."
fi

# Step 3: Activate virtual environment
echo "⚡ Activating virtual environment..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Step 4: Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies
if [ -f "requirements.txt" ]; then
  echo "📦 Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
else
  echo "⚠️ requirements.txt not found. Skipping dependency installation."
fi

echo "✅ Environment setup complete!"
echo "To activate later, run: source $VENV_DIR/bin/activate"
