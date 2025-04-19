# Survey Metrics Deployment Guide

This document provides comprehensive instructions for deploying and maintaining the Survey Metrics application on PythonAnywhere.

## Initial Deployment

### Prerequisites
- PythonAnywhere account
- Git repository access
- Basic knowledge of Django and Python

### Account Setup
1. Register at [PythonAnywhere.com](https://www.pythonanywhere.com/)
2. Log in to your account
3. Go to the Web tab and click "Add a new web app"
4. Choose "Manual configuration" (not Django)
5. Select Python 3.12
6. Note your domain: prudhvi19.pythonanywhere.com

### Code Deployment
1. Open a Bash console from the Consoles tab
2. Clone the repository:
   ```
   git clone https://github.com/vinay9977/InsightFlow.git
   ```
3. Set up virtual environment:
   ```
   cd ~/survey_metrics_app
   python -m venv venv
   source venv/bin/activate
   pip install Django
   ```

### Production Settings
1. Create a production settings file:
   ```
   mkdir -p ~/survey_metrics_app/survey/survey
   nano ~/survey_metrics_app/survey/survey/production_settings.py
   ```
2. Add the following content:
   ```python
   from survey.settings import *
   import os

   # Production settings
   DEBUG = False

   # Use a secure random string (generate one at https://djecrety.ir/)
   SECRET_KEY = 'generate-a-new-secret-key-and-put-it-here'

   # Allow your PythonAnywhere domain
   ALLOWED_HOSTS = ['Vinay77.pythonanywhere.com']

   # Security settings
   SECURE_CONTENT_TYPE_NOSNIFF = True
   SECURE_BROWSER_XSS_FILTER = True
   X_FRAME_OPTIONS = 'DENY'

   # Static files
   STATIC_ROOT = '/home/Vinay77/survey_metrics_app/survey/staticfiles'
   STATIC_URL = '/static/'

   # SQLite database configuration (will be replaced in User Story 2)
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
       }
   }
   ```

### Database Setup
1. Run migrations:
   ```
   cd ~/survey_metrics_app/survey
   python manage.py migrate --settings=survey.production_settings
   ```
2. Create superuser:
   ```
   python manage.py createsuperuser --settings=survey.production_settings
   ```
   Follow the prompts to create an admin account.

### WSGI Configuration
1. Go to the "Web" tab in PythonAnywhere
2. Look for the WSGI configuration file section and click the link to edit the WSGI file
3. Replace the content with:
   ```python
   import os
   import sys

   # Add the project directory to the system path
   path = '/home/Vinay77/survey_metrics_app/survey'
   if path not in sys.path:
       sys.path.insert(0, path)

   # Set the Django settings module
   os.environ['DJANGO_SETTINGS_MODULE'] = 'survey.production_settings'

   # Import Django's WSGI functionality
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
4. Save the file

### Static Files Configuration
1. In the "Web" tab, go to the "Static files" section
2. Add a new static files mapping:
   - URL: `/static/`
   - Directory: `/home/Vinay77/survey_metrics_app/survey/staticfiles`
3. Collect static files:
   ```
   cd ~/survey_metrics_app/survey
   python manage.py collectstatic --settings=survey.production_settings
   ```

### Finalize Deployment
1. Go to the "Web" tab and click the "Reload" button for your web app
2. Visit your site at Vinay77.pythonanywhere.com
3. Log in to the admin interface at Vinay77.pythonanywhere.com/admin

## Updating the Application

When you need to deploy new code or make changes to the existing deployment, follow these steps:

### 1. Pull the Latest Code Changes
```bash
# Connect to PythonAnywhere's bash console
cd ~/survey_metrics_app
git pull origin main  # or master, depending on your branch name
```

### 2. Update Dependencies (if necessary)
```bash
# Activate your virtual environment
source ~/survey_metrics_app/venv/bin/activate


### 3. Apply Database Migrations (if necessary)
```bash
cd ~/survey_metrics_app/survey
python manage.py migrate --settings=survey.production_settings
```

### 4. Update Static Files (if necessary)
```bash
cd ~/survey_metrics_app/survey
python manage.py collectstatic --noinput --settings=survey.production_settings
```

### 5. Reload the Web Application
1. Go to the PythonAnywhere dashboard
2. Navigate to the "Web" tab
3. Click the "Reload" button for your web app

## Troubleshooting

### Common Issues and Solutions

#### Application Returns 500 Error
1. Check the error logs in the PythonAnywhere Web tab
2. Verify that all migrations have been applied
3. Check file permissions for the SQLite database
4. Ensure your virtual environment has all required dependencies

#### Static Files Not Loading
1. Verify static files settings in production_settings.py
2. Make sure you've run the collectstatic command
3. Check the static files mapping in the PythonAnywhere Web tab

#### Database Issues
1. Check if migrations have been applied correctly
2. Verify database file permissions (for SQLite)
3. Try connecting to the database manually to test connectivity

#### DisallowedHost Error
1. Verify that ALLOWED_HOSTS in production_settings.py includes your domain
2. Make sure you're using the correct settings file (production_settings.py)

### Checking Logs
- Access error logs through the PythonAnywhere Web tab
- For more detailed logs, add logging configuration to your settings file

## Backup and Restore

### Database Backup
```bash
# For SQLite database
cd ~/survey_metrics_app/survey
cp db.sqlite3 db.sqlite3.backup
```

### Code Backup
Your code is already versioned with Git, but you can create a snapshot:
```bash
cd ~/survey_metrics_app
git add .
git commit -m "Backup before [operation]"
```

## Security Considerations

- Regularly update Django and dependencies
- Keep your SECRET_KEY secure and unique
- Set DEBUG = False in production
- Use HTTPS when possible
- Run security checks with `python manage.py check --deploy`
