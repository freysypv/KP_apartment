from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import KPPasswordResetForm, KPSetPasswordForm, LoginForm
from .forms import SignUpForm
from django.contrib.auth import login
from django.shortcuts import redirect, render

app_name = "core"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("amenities/", views.AmenitiesView.as_view(), name="amenities"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("gallery/", views.GalleryView.as_view(), name="gallery"),

    path("login/", auth_views.LoginView.as_view(
        template_name="core/auth/login.html",
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.signup, name="signup"),

    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name="core/auth/password_reset.html",
        form_class=KPPasswordResetForm,
        email_template_name="core/auth/password_reset_email.txt",
        subject_template_name="core/auth/password_reset_subject.txt",
        success_url=reverse_lazy("core:password_reset_done"),
    ), name="password_reset"),

    path("password-reset/sent/", auth_views.PasswordResetDoneView.as_view(
        template_name="core/auth/password_reset_done.html",
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="core/auth/password_reset_confirm.html",
        form_class=KPSetPasswordForm,
        success_url=reverse_lazy("core:password_reset_complete"),
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="core/auth/password_reset_complete.html",
    ), name="password_reset_complete"),

    
]

def signup(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            return redirect("core:home")
    else:
        form = SignUpForm()
    return render(request, "core/auth/signup.html", {"form": form})