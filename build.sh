#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
python -m pip install -r requirements.txt

# Collect static assets for WhiteNoise
python manage.py collectstatic --no-input

# Run database schema migrations
python manage.py migrate

# Seed hospital operatories, catalog, users, demo charts, and appointments
python manage.py seed_data
