# Survey Metrics Project Installation Guide

## Prerequisites
- Python 3.12
- Conda package manager
- Git

## Installation Steps

### Step 1: Create a Conda Environment
```bash
conda create -n survey_metrics_spm python=3.12
conda activate survey_metrics_spm
```

### Step 2: Clone the Repository
```bash
git clone https://bitbucket.org/korrv01/survey_metrics/src/main/
cd <directory-name>
```

### Step 3: Install Dependencies
```bash
python -m pip install Django
```
Apply Migrations : python manage.py migrate  
### Step 4: Run the Development Server
```bash
python manage.py runserver
```
The application will be available at: http://127.0.0.1:8000/

### Step 5: Create Superuser Account
```bash
python manage.py createsuperuser
```
Access the admin panel at: http://127.0.0.1:8000/admin/

## Test Accounts

### Regular User Account
- Email: test@gmail.com
- Password: test
- *Created through signup feature*

### Admin Account
- Username: admintest
- Password: admintest
- *Created through createsuperuser command*
