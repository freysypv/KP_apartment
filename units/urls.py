from django.urls import path

from . import views

app_name = "units"

urlpatterns = [
    path("", views.UnitListView.as_view(), name="list"),
    path("<int:pk>/", views.UnitDetailView.as_view(), name="detail"),
]
