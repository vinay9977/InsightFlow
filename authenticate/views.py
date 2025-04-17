from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import re

def login_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login/')

def validate_password_complexity(password):
    """
    Validates password complexity requirements
    Returns (bool, str) tuple - (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must include at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must include at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must include at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must include at least one special character"
    
    return True, ""

def register(request):
    if request.method == 'POST':
        # Validate required fields
        required_fields = ['fname', 'lname', 'email', 'cpass', 'cnpass']
        if not all(request.POST.get(field) for field in required_fields):
            return render(request, 'signup.html', {"error": "All fields are required"})

        # Validate email format
        email = request.POST.get("email")
        if '@' not in email or '.' not in email:
            return render(request, 'signup.html', {"error": "Invalid email format"})

        # Check if email exists
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {"error": "Email already exists"})

        password = request.POST.get("cpass")
        confirm_password = request.POST.get("cnpass")

        # Validate password complexity
        is_valid, error_message = validate_password_complexity(password)
        if not is_valid:
            return render(request, 'signup.html', {"error": error_message})

        # Check if passwords match - Updated error message to match test case
        if password != confirm_password:
            return render(request, 'signup.html', {"error": "Password doesn't match"})

        try:
            User.objects.create_user(
                first_name=request.POST.get("fname"),
                last_name=request.POST.get("lname"),
                email=email,
                username=email,
                password=password
            )
            return HttpResponseRedirect('/login/')
        except Exception as e:
            return render(request, 'signup.html', {"error": str(e)})
            
    return render(request, 'signup.html')

def auth_user(request):
    if request.method == 'POST':
        email = request.POST.get('username', '').lower().strip()
        password = request.POST.get('password', '')
        
        # Validate input fields
        if not email or not password:
            return render(request, 'login.html', {
                'error': 'Please enter both email and password',
                'email': email
            })
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return render(request, 'login.html', {
                'error': 'Invalid email format',
                'email': email
            })
        
        try:
            # Try to get user with case-insensitive email
            user = User.objects.get(email__iexact=email)
            # Now authenticate with the correct username
            auth_user = authenticate(
                username=user.username,
                password=password
            )
            if auth_user:
                login(request, auth_user)
                return HttpResponseRedirect('/')
            else:
                # Invalid password
                return render(request, 'login.html', {
                    'error': 'Invalid email or password',
                    'email': email
                })
        except User.DoesNotExist:
            # User not found
            return render(request, 'login.html', {
                'error': 'Invalid email or password',
                'email': email
            })
    
    # If GET request, just show the login page
    return render(request, 'login.html')

def register_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request, 'signup.html')