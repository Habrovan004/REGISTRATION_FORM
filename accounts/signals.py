from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from .models import CustomUser
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

@receiver(post_save, sender=CustomUser)
def send_activation_email(sender, instance, created, **kwargs):
    if created and not instance.is_active:
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        token = default_token_generator.make_token(instance)
        activation_link = f"{settings.SITE_URL}{reverse('activate', kwargs={'uidb64': uid, 'token': token})}"
        subject = "Activate Your Account"
        message = f"Hi {instance.username},\n\nPlease click the link below to activate your account:\n{activation_link}"
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])
