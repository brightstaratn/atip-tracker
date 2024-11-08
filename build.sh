#!/usr/bin/env bash

set -o errexit  # Exit immediately if a command exits with a non-zero status.

# Activate virtual environment if you're using one
# source venv/bin/activate  # Uncomment if using a virtual env

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
python manage.py migrate

# Optional: Run tests
# python manage.py test
