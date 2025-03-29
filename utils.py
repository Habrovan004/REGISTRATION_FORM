from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_activation_email(user, activation_link):
    """
    Sends an account activation email to the user.
    """
    subject = settings.ACCOUNT_ACTIVATION_SUBJECT
    template_path = settings.ACCOUNT_ACTIVATION_TEMPLATE
    message = render_to_string(template_path, {'user': user, 'activation_link': activation_link})
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
