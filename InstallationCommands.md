InsightFlow Project Installation Guide
Prerequisites
Python 3.12
Conda package manager
Git
Installation Steps
Step 1: Create a Conda Environment
conda create -n InsightFlow
conda activate InsightFlow
Step 2: Clone the Repository
git clone https://github.com/vinay9977/InsightFlow.git
cd <directory-name>
Step 3: Install Dependencies
python -m pip install Django
Step 4: Run the Development Server
python manage.py runserver
The application will be available at: http://127.0.0.1:8000/
Step 5: Create Superuser Account
python manage.py createsuperuser
Access the admin panel at: http://127.0.0.1:8000/admin/
Test Accounts
Regular User Account
Email: test@gmail.com
Password: test
Created through signup feature
Admin Account
Username: admintest
Password: admintest
Created through createsuperuser command
