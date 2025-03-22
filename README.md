# InsightFlow: A User-Friendly Platform for Psychological Surveys


## Introduction

**InsightFlow** is a full-stack survey platform designed for creating, managing, and analyzing psychological surveys. Built with Django, it provides secure authentication, data collection, and reporting features for researchers and participants. This documentation is a quick guide to getting the project running locally.

> **Note:** This project is currently in the initial stage of development and may undergo significant changes.

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

- Python 3.10+
- Django 5+
- Pip
- Virtualenv (optional)

## Installation

1. Clone the Repository:

   ```bash
   git clone https://github.com/vinay9977/InsightFlow.git
   cd InsightFlow
   ```

2. Set Up the Environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set Up the Database:

   ```bash
   python manage.py migrate
   ```

4. Create a superuser if needed:

   ```bash
   python manage.py createsuperuser
   ```

5. Run the Development Server:

   ```bash
   python manage.py runserver
   ```

   Access the app at: `http://127.0.0.1:8000`

## Test Accounts

| Account Type     | Username/Email   | Password   |
|------------------|------------------|------------|
| **Regular User** | test@gmail.com   | test       |
| **Admin User**   | admintest        | admintest  |