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
    errors = []
    
    if len(password) < 8:
        errors.append("8 characters")
    
    if not re.search(r'[A-Z]', password):
        errors.append("an uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("a lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("a number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("a special character")
    
    if errors:
        return False, "Password must include at least:<br>- " + "<br>- ".join(errors)
    
    return True, ""

def register(request):
    if request.method == 'POST':
        # Get form data
        form_data = {
            'fname': request.POST.get('fname', ''),
            'lname': request.POST.get('lname', ''),
            'email': request.POST.get('email', ''),
            'mno': request.POST.get('mno', '')
        }
        
        # Collect all validation errors
        errors = []
        
        # Validate required fields - we now handle this more specifically
        # and with client-side validation, so no generic message needed
        
        # Validate email format if provided
        email = request.POST.get("email")
        if email:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Invalid email format")
            
            # Check if email exists
            elif User.objects.filter(email=email).exists():
                errors.append("Email already exists")
        
        # Validate password if provided
        password = request.POST.get("cpass")
        confirm_password = request.POST.get("cnpass")
        
        if password:
            # Validate password complexity
            is_valid, error_message = validate_password_complexity(password)
            if not is_valid:
                errors.append(error_message)
            
            # Check if passwords match
            if confirm_password and password != confirm_password:
                errors.append("Passwords don't match")
        
        # If there are any validation errors, show them all
        if errors:
            # If there's only a password error, just show that with its formatting
            if len(errors) == 1 and "Password must include" in errors[0]:
                return render(request, 'signup.html', {
                    "error": errors[0], 
                    **form_data
                })
            # Otherwise combine with semicolons
            else:
                error_message = "; ".join(errors)
                return render(request, 'signup.html', {
                    "error": error_message, 
                    **form_data
                })
        
        # If all validation passes, create the user
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
            return render(request, 'signup.html', {"error": str(e), **form_data})
            
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