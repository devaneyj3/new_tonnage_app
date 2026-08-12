#!/bin/bash

# 1. Create a virtual environment named 'venv'
echo "Creating virtual environment..."
python3 -m venv venv

# 2. Upgrade pip inside the environment
echo "Upgrading pip..."
./venv/bin/pip install --upgrade pip

# 3. Install the required packages
echo "Installing dependencies from requirements.txt..."
./venv/bin/pip install -r requirements.txt

echo "Setup complete! To activate your environment, run: source venv/bin/activate"
