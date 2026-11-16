from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from announcements.models import Announcement
from maintenance.models import MaintenanceRequest

from .models import Lease


def get_active_lease(user):
    return (
        Lease.objects.filter(tenant=user, is_active=True)
        .select_related("unit")
        .first()
    )


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "leases/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["lease"] = get_active_lease(user)
        ctx["open_requests"] = (
            MaintenanceRequest.objects.filter(tenant=user)
            .exclude(status=MaintenanceRequest.Status.RESOLVED)
            .select_related("unit")[:5]
        )
        ctx["announcements"] = Announcement.objects.filter(is_published=True)[:3]
        return ctx


class MyLeaseView(LoginRequiredMixin, TemplateView):
    template_name = "leases/my_lease.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["lease"] = get_active_lease(self.request.user)
        return ctx