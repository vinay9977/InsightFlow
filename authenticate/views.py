from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
# Create your views here.

def login_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request,'login.html')

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/login')

def register(request):
    if request.POST.get("cpass") == request.POST.get("cnpass"):
        User.objects.create_user(
            first_name=request.POST.get("fname"),
            last_name=request.POST.get("lname"),
            email=request.POST.get("email"),
            username=request.POST.get("email"),
            password=request.POST.get("cpass")
        )
        return HttpResponseRedirect('/login')
    else:
        return render(request,'signup.html',{"error":"Password dosen't match"})

def auth_user(request):
    if request.method == 'POST':
        user = authenticate(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request,user)
            return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/login')

def register_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')
    return render(request,'signup.html')