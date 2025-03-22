# InsightFlow: A User-Friendly Platform for Psychological Surveys


## Introduction

**InsightFlow** is a Django-based web application for managing surveys. This documentation provides a quick guide to getting the project running locally.

## Project Structure

```
/
├── README.md                # Documentation
├── survey/                  # Survey application
├── authenticate/            # Authentication-related code
├── db.sqlite3               # SQLite database
├── manage.py                # Entry point for Django commands
└── requirements.txt         # Project dependencies
```

## Prerequisites

- **Python 3.13+**
- **Django**
- **pip**
- **Virtualenv** (optional)

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/vinay9977/InsightFlow.git
   cd InsightFlow
   ```

2. **Set Up the Environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set Up the Database:**

   ```bash
   python manage.py migrate
   ```

4. **Create Superuser:**

   ```bash
   python manage.py createsuperuser
   ```

5. **Run the Development Server:**

   ```bash
   python manage.py runserver
   ```

   Access the app at: `http://127.0.0.1:8000`

## Test Accounts

| Account Type     | Username/Email   | Password   |
|------------------|------------------|------------|
| **Regular User** | test@gmail.com   | test       |
| **Admin User**   | admintest        | admintest  |