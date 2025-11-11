#!/bin/bash
# Deployment preparation script

echo "Preparing application for Render deployment..."

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify Django installation
python -c "import django; print('Django version:', django.get_version())" || { echo "Django is not installed properly"; exit 1; }

echo "Django installation verified!"

# Run migrations (these would be run in the deployment process)
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Deployment preparation complete!"
echo "Remember: Do not commit your .env file to GitHub."
echo "Set environment variables in the Render dashboard."