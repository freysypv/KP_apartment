from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from leases.models import Lease

from .form import MaintenanceRequestForm
from .models import MaintenanceRequest


class MyRequestsView(LoginRequiredMixin, ListView):
    template_name = "core/maintenance/request_list.html"
    context_object_name = "requests"

    def get_queryset(self):
        return MaintenanceRequest.objects.filter(tenant=self.request.user).select_related("unit")


class NewRequestView(LoginRequiredMixin, CreateView):
    form_class = MaintenanceRequestForm
    template_name = "core/maintenance/request_form.html"
    success_url = reverse_lazy("maintenance:list")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.lease = (
                Lease.objects.filter(tenant=request.user, is_active=True)
                .select_related("unit").first()
            )
            if self.lease is None:
                messages.error(request, "You need an active lease to submit a maintenance request.")
                return redirect("leases:my_lease")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["unit"] = self.lease.unit
        return ctx

    def form_valid(self, form):
        form.instance.tenant = self.request.user
        form.instance.unit = self.lease.unit
        messages.success(self.request, "Your request was submitted.")
        return super().form_valid(form)