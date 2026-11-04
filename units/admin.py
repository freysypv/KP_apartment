from django.contrib import admin

from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("number", "floor", "bedrooms", "bathrooms", "square_feet", "monthly_rent", "status")
    list_filter = ("status", "bedrooms", "floor")
    search_fields = ("number", "description")
    list_editable = ("status",)
