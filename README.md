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
├── cypress/                 # Tests
├── db.sqlite3               # SQLite database
├── manage.py                # Entry point for Django commands
└── requirements.txt         # Project dependencies
```

## Prerequisites

- Python 3.10+
- Django 5+
- Pip
- Cypress
- Virtualenv (optional)

## Installation

1. Clone the Repository:

   ```bash
   git clone https://github.com/vinay9977/InsightFlow.git
   cd InsightFlow
   ```

2. Set Up the Environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Run the Development Server:

   ```bash
   python manage.py runserver
   ```

   Access the app at: `http://127.0.0.1:8000`. Use one of the test accounts below or create a new one.

## Test Accounts

| Account Type     | Username/Email   | Password   |
|------------------|------------------|------------|
| **Regular User** | test@gmail.com   | test       |
| **Admin User**   | admintest        | admintest  |

## Additional Options

- Database Migration:

   ```bash
   python manage.py migrate
   ```

- Create a Superuser:

   ```bash
   python manage.py createsuperuser
   ```

## Running Tests

We use Cypress for end-to-end testing of the application, focusing on the authentication functionality:
- Regular user login
- Admin user login
- Invalid login attempts

### Running Cypress Tests Locally

1. Make sure your Django server is running:
   ```bash
   source venv/bin/activate
   python3 manage.py runserver
   ```

2. In a separate terminal, run Cypress tests:
   ```bash
   npm run cypress:open   # For interactive test runner
   # OR
   npm run cypress:run    # For headless testing
   ```

## Continuous Integration

This project uses GitHub Actions for continuous integration. On every push to main/master branches and pull requests, the workflow:

1. Sets up the Python environment
2. Installs dependencies
3. Creates test users
4. Runs the Cypress login tests against a Django test server

The configuration is defined in `.github/workflows/cypress-tests.yml`.

## License

This project is licensed under the [MIT License](LICENSE).