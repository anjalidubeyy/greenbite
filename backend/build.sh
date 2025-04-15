#!/bin/bash
set -e

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install wheel first
pip install wheel

# Install numpy first (it's a dependency for other packages)
pip install numpy==1.21.2

# Install other requirements
pip install -r requirements.txt

# Install the package in development mode
pip install -e .

# Install gunicorn
pip install gunicorn 