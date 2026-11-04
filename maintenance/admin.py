

# Register your models here.
from django.contrib import admin

from .models import MaintenanceRequest


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ("title", "unit", "tenant", "category", "priority", "status", "created_at")
    list_filter = ("status", "priority", "category")
    search_fields = ("title", "description", "unit__number", "tenant__username")
    list_editable = ("status",)
    readonly_fields = ("created_at", "updated_at")