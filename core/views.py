from django.contrib import messages
from django.contrib.auth import login
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ContactForm, SignUpForm


class HomeView(TemplateView):
    template_name = "core/home.html"


class AmenitiesView(TemplateView):
    template_name = "core/amenities.html"


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(FormView):
    template_name = "core/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("core:contact")

    def form_valid(self, form):
        data = form.cleaned_data
        send_mail(
            subject=f"KP Apartments inquiry from {data['name']}",
            message=(
                f"From: {data['name']} <{data['email']}>\n"
                f"Phone: {data['phone']}\n\n"
                f"{data['message']}"
            ),
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=["office@kpapartments.com"],  # change to your address
        )
        messages.success(self.request, "Thanks! We got your message and will reply soon.")
        return super().form_valid(form)


class GalleryView(TemplateView):
    template_name = "core/gallery.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["items"] = [
            # Exterior
            {"title": "Front Entrance", "category": "exterior", "image": "https://picsum.photos/seed/kp-ext1/800/600"},
            {"title": "Setting Area", "category": "exterior", "image": "https://picsum.photos/seed/kp-ext2/800/600"},
            {"title": "Play Area", "category": "exterior", "image": "https://picsum.photos/seed/kp-ext3/800/600"},
            {"title": "Parking Area", "category": "exterior", "image": "https://picsum.photos/seed/kp-ext4/800/600"},
            {"title": "Garden Area", "category": "exterior", "image": "https://picsum.photos/seed/kp-ext5/800/600"},
            # Interior
            {"title": "Living Room", "category": "interior", "image": "https://picsum.photos/seed/kp-int1/800/600"},
            {"title": "Kitchen", "category": "interior", "image": "https://picsum.photos/seed/kp-int2/800/600"},
            {"title": "Bedroom", "category": "interior", "image": "https://picsum.photos/seed/kp-int3/800/600"},
            {"title": "Bathroom", "category": "interior", "image": "https://picsum.photos/seed/kp-int4/800/600"},
            {"title": "Dining Room", "category": "interior", "image": "https://picsum.photos/seed/kp-int5/800/600"},
            # Floor plans
            {"title": "1 Bed / 1 Bath", "category": "floorplan", "image": "https://picsum.photos/seed/kp-fp1/800/600"},
            {"title": "2 Bed / 1 Bath", "category": "floorplan", "image": "https://picsum.photos/seed/kp-fp2/800/600"},
            {"title": "Common Area", "category": "floorplan", "image": "https://picsum.photos/seed/kp-fp3/800/600"},
        ]
        return context


# Sign up view for new user registration
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