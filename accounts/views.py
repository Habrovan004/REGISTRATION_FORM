from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.sites.shortcuts import get_current_site
from .utils.token_generator import account_activation_token
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import logging
from django.contrib.auth.tokens import default_token_generator
from .models import CustomUser

logger = logging.getLogger(__name__)
User = get_user_model()

def home_view(request):
    """Render the home page"""
    return render(request, 'accounts/home.html')

def signup_view(request):
    """Handle user registration with email verification"""
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password1', '').strip()
        password2 = request.POST.get('password2', '').strip()
        
        # Validate inputs
        if not all([email, password, password2]):
            messages.error(request, 'All fields are required.')
            return redirect('signup')
            
        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('signup')
            
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return redirect('signup')
            
        if User.objects.filter(email=email).exists():
            messages.error(request, 'This email is already registered.')
            return redirect('signup')

        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                is_active=False  # Critical for email verification
            )
            
            # Generate activation token
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            
            # Prepare and send email
            mail_subject = 'Activate Your Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'protocol': protocol,
                'uid': uid,
                'token': token,
            })
            
            try:
                send_mail(
                    subject=mail_subject,
                    message=message,
                    from_email=None,  # Uses DEFAULT_FROM_EMAIL
                    recipient_list=[email],
                    fail_silently=False
                )
                logger.info(f"Activation email sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {str(e)}", exc_info=True)
                messages.error(request, 'Failed to send activation email. Please try again later.')
                return redirect('signup')
            
            messages.success(request, 'We sent you an activation email. Please check your inbox.')
            return redirect('login')  # Redirect to login page after signup
            
        except Exception as e:
            logger.error(f"Signup error for {email}: {str(e)}", exc_info=True)
            messages.error(request, 'Registration failed. Please try again later.')
            return redirect('signup')
    
    return render(request, 'accounts/signup.html')

def login_view(request):
    """Handle user login with proper authentication"""
    if request.user.is_authenticated:
        return redirect('home')  # Redirect to home page after login
        
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.email}!')
                next_url = request.POST.get('next') or settings.LOGIN_REDIRECT_URL
                return redirect(next_url)
            else:
                messages.error(
                    request,
                    'Account not activated. Please check your email for the activation link.'
                )
                return render(request, 'accounts/login.html', {
                    'form': form,
                    'inactive_user': True,
                    'email': user.email,
                    'next': next_url
                })
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url
    })

def logout_view(request):
    """Handle user logout securely"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def activate(request, uidb64, token):
    """Handle account activation link"""
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
        
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        logger.error(f"Activation error: {str(e)}", exc_info=True)
        user = None
    
    if user is not None and account_activation_token.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, 'Your account has been activated successfully!')
        else:
            messages.info(request, 'Your account is already active.')
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    messages.error(request, 'Activation link is invalid or has expired.')
    return redirect('signup')

def resend_activation(request):
    """Handle resending activation emails"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                token = account_activation_token.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                send_mail(
                    subject='Activate Your Account',
                    message=render_to_string('accounts/account_activation_email.html', {
                        'user': user,
                        'domain': current_site.domain,
                        'protocol': protocol,
                        'uid': uid,
                        'token': token,
                    }),
                    from_email=None,
                    recipient_list=[email],
                    fail_silently=False
                )
                messages.success(request, 'New activation email sent! Please check your inbox.')
            else:
                messages.info(request, 'Account is already active. Please login.')
        except ObjectDoesNotExist:
            messages.error(request, 'No account found with this email.')
        except Exception as e:
            logger.error(f"Resend activation error for {email}: {str(e)}", exc_info=True)
            messages.error(request, 'Failed to resend activation email. Please try again later.')
    
    return redirect('login')

def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('login')  # Redirect to login page after activation
    else:
        return render(request, 'accounts/activation_invalid.html')