#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations (if using Django)
echo "Running migrations..."
python manage.py migrate
if [[ $CREATE_SUPERUSER ]];
then
  python manage.py createsuperuser --no-input --email $DJANGO_SUPERUSER_EMAIL --username $SUPERUSER_USERNAME

# Collect static files (if using Django)
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Build completed successfully."
