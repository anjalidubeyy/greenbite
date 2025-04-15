#!/bin/bash
set -e

# Upgrade pip
python -m pip install --upgrade pip

# Install wheel first
pip install wheel

# Install requirements using the setup.py
pip install -e .

# Install gunicorn
pip install gunicorn 