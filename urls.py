from django.urls import path
from . import views
from .views import login_view

urlpatterns = [
    path("register/", views.register_user, name="register_user"),
    path("activate/<uidb64>/<token>/", views.activate_account, name="activate_account"),
    path("login/", login_view, name="login"),
]
