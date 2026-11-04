from django.views.generic import DetailView, ListView

from .models import Unit


class UnitListView(ListView):
    model = Unit
    template_name = "units/unit_list.html"
    context_object_name = "units"

    def get_queryset(self):
        qs = Unit.objects.all()
        # Show only available units unless ?all=1
        if not self.request.GET.get("all"):
            qs = qs.filter(status=Unit.Status.AVAILABLE)
        beds = self.request.GET.get("beds")
        if beds and beds.isdigit():
            qs = qs.filter(bedrooms=int(beds))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["beds"] = self.request.GET.get("beds", "")
        ctx["show_all"] = bool(self.request.GET.get("all"))
        ctx["bedroom_options"] = (
            Unit.objects.order_by("bedrooms").values_list("bedrooms", flat=True).distinct()
        )
        return ctx


class UnitDetailView(DetailView):
    model = Unit
    template_name = "units/unit_detail.html"
    context_object_name = "unit"
