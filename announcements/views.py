from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Announcement


class AnnouncementListView(LoginRequiredMixin, ListView):
    template_name = "core/announcements/announcement_list.html"
    context_object_name = "announcements"

    def get_queryset(self):
        return Announcement.objects.filter(is_published=True)