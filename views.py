from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .utils import send_activation_email

def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = False  # Deactivate account until activation
        user.save()
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        activation_link = request.build_absolute_uri(
            reverse("activate_account", kwargs={"uidb64": uid, "token": token})
        )
        
        # Send activation email
        send_activation_email(user, activation_link)
        
        return render(request, "registration/registration_success.html")
    return render(request, "registration/register.html")

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse("Your account has been activated successfully!")
    else:
        return HttpResponse("Activation link is invalid!")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to the 'home' page
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')  # Render the login page
