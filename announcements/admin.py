from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("title", "is_pinned", "is_published", "author", "created_at")
    list_filter = ("is_pinned", "is_published")
    search_fields = ("title", "body")
    readonly_fields = ("author", "created_at")

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
