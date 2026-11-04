from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from units.models import Unit


class Lease(models.Model):
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="leases"
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="leases")
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(max_digits=8, decimal_places=2)
    security_deposit = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.tenant} - {self.unit} ({self.start_date} to {self.end_date})"

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError({"end_date": "End date must be after the start date."})
        if self.is_active and self.unit_id:
            overlapping = Lease.objects.filter(unit=self.unit, is_active=True).exclude(pk=self.pk)
            if overlapping.exists():
                raise ValidationError("This unit already has an active lease.")

    def save(self, *args, **kwargs):
        # Default the rent to the unit's listed rent when left blank
        if self.monthly_rent is None and self.unit_id:
            self.monthly_rent = self.unit.monthly_rent
        super().save(*args, **kwargs)
        self._sync_unit_status()

    def _sync_unit_status(self):
        unit = self.unit
        if unit.status == Unit.Status.MAINTENANCE:
            return
        has_active = unit.leases.filter(is_active=True).exists()
        new_status = Unit.Status.OCCUPIED if has_active else Unit.Status.AVAILABLE
        if unit.status != new_status:
            unit.status = new_status
            unit.save(update_fields=["status"])
