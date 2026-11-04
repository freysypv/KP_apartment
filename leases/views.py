from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import Lease


class MyLeaseView(LoginRequiredMixin, TemplateView):
    template_name = "leases/my_lease.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["lease"] = (
            Lease.objects.filter(tenant=self.request.user, is_active=True)
            .select_related("unit")
            .first()
        )
        return ctx
