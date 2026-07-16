from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from .models import UserProfile

def register(request):
    """User registration view"""
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.is_approved = False
            user.profile.save()
            messages.info(request, 'Account created! Wait for admin approval to login.')
            return redirect('accounts:login')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.profile.is_approved:
                login(request, user)
                return redirect('cattle:dashboard')
            else:
                messages.error(request, 'Your account is pending admin approval. Please wait.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    # Create a form for GET requests
    form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})
# Create your views here.
