from django.urls import path

from . import views

app_name = "maintenance"

urlpatterns = [
    path("", views.MyRequestsView.as_view(), name="list"),
    path("new/", views.NewRequestView.as_view(), name="new"),
]