from django.urls import path

from . import views

app_name = "leases"

urlpatterns = [
    path("my-lease/", views.MyLeaseView.as_view(), name="my_lease"),
]
