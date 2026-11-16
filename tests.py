from django.test import TestCase

# Create your tests here.
from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from django.urls import reverse

from leases.models import Lease
from maintenance.models import MaintenanceRequest
from units.models import Unit


class DashboardTests(TestCase):
    def setUp(self):
        from announcements.models import Announcement
        from maintenance.models import MaintenanceRequest

        self.Announcement = Announcement
        self.MaintenanceRequest = MaintenanceRequest
        User = get_user_model()
        self.tenant = User.objects.create_user("tenant", password="pw12345!")
        self.other = User.objects.create_user("other", password="pw12345!")
        self.unit = Unit.objects.create(number="101", square_feet=700, monthly_rent=1200)
        Lease.objects.create(
            tenant=self.tenant, unit=self.unit,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), monthly_rent=1200,
        )
        self.url = reverse("leases:dashboard")

    def test_dashboard_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_dashboard_shows_the_tenants_lease(self):
        self.client.login(username="tenant", password="pw12345!")
        self.assertContains(self.client.get(self.url), "Unit 101")

    def test_dashboard_without_lease_shows_message(self):
        self.client.login(username="other", password="pw12345!")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No active lease on file")

    def test_dashboard_lists_open_requests_but_not_resolved_ones(self):
        self.MaintenanceRequest.objects.create(
            tenant=self.tenant, unit=self.unit, title="Leaky sink", description="x"
        )
        self.MaintenanceRequest.objects.create(
            tenant=self.tenant, unit=self.unit, title="Fixed door", description="x",
            status=self.MaintenanceRequest.Status.RESOLVED,
        )
        self.client.login(username="tenant", password="pw12345!")
        response = self.client.get(self.url)
        self.assertContains(response, "Leaky sink")
        self.assertNotContains(response, "Fixed door")

    def test_dashboard_shows_published_announcements_only(self):
        self.Announcement.objects.create(title="Pool open", body="x")
        self.Announcement.objects.create(title="Hidden note", body="x", is_published=False)
        self.client.login(username="tenant", password="pw12345!")
        response = self.client.get(self.url)
        self.assertContains(response, "Pool open")
        self.assertNotContains(response, "Hidden note")

    def test_login_redirects_to_dashboard(self):
        response = self.client.post(
            reverse("core:login"), {"username": "tenant", "password": "pw12345!"}
        )
        self.assertRedirects(response, self.url)


class LeaseTests(TestCase):
    def setUp(self):
        self.tenant = get_user_model().objects.create_user("tenant", password="pw12345!")
        self.unit = Unit.objects.create(number="101", square_feet=700, monthly_rent=1200)

    def make_lease(self, **overrides):
        data = dict(
            tenant=self.tenant, unit=self.unit,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            monthly_rent=1200,
        )
        data.update(overrides)
        return Lease(**data)

    def test_creating_a_lease_marks_unit_occupied(self):
        self.make_lease().save()
        self.unit.refresh_from_db()
        self.assertEqual(self.unit.status, Unit.Status.OCCUPIED)

    def test_second_active_lease_on_same_unit_is_rejected(self):
        self.make_lease().save()
        with self.assertRaises(ValidationError):
            self.make_lease().full_clean()

    def test_end_date_must_be_after_start_date(self):
        with self.assertRaises(ValidationError):
            self.make_lease(end_date=date(2025, 1, 1)).full_clean()






# unit test




class UnitModelTests(TestCase):
    def test_str_shows_unit_number(self):
        unit = Unit.objects.create(number="101", square_feet=700, monthly_rent=1200)
        self.assertEqual(str(unit), "Unit 101")

    def test_new_unit_defaults_to_available(self):
        unit = Unit.objects.create(number="102", square_feet=700, monthly_rent=1200)
        self.assertEqual(unit.status, Unit.Status.AVAILABLE)
        self.assertTrue(unit.is_available)

    def test_occupied_unit_is_not_available(self):
        unit = Unit.objects.create(
            number="103", square_feet=700, monthly_rent=1200, status=Unit.Status.OCCUPIED
        )
        self.assertFalse(unit.is_available)


class UnitViewTests(TestCase):
    def setUp(self):
        self.available = Unit.objects.create(
            number="201", bedrooms=1, square_feet=700, monthly_rent=1200
        )
        self.occupied = Unit.objects.create(
            number="202", bedrooms=2, square_feet=950, monthly_rent=1500,
            status=Unit.Status.OCCUPIED,
        )

    def test_list_page_loads_without_login(self):
        response = self.client.get(reverse("units:list"))
        self.assertEqual(response.status_code, 200)

    def test_list_shows_only_available_units_by_default(self):
        response = self.client.get(reverse("units:list"))
        self.assertContains(response, "Unit 201")
        self.assertNotContains(response, "Unit 202")

    def test_list_can_include_occupied_units(self):
        response = self.client.get(reverse("units:list"), {"all": "1"})
        self.assertContains(response, "Unit 202")

    def test_list_filters_by_bedrooms(self):
        response = self.client.get(reverse("units:list"), {"all": "1", "beds": "2"})
        self.assertContains(response, "Unit 202")
        self.assertNotContains(response, "Unit 201")

    def test_detail_page_shows_the_unit(self):
        response = self.client.get(reverse("units:detail", args=[self.available.pk]))
        self.assertContains(response, "Unit 201")

    def test_detail_page_for_missing_unit_is_404(self):
        response = self.client.get(reverse("units:detail", args=[9999]))
        self.assertEqual(response.status_code, 404)                    





# maintenance tests




class MaintenanceTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.tenant = User.objects.create_user("tenant", password="pw12345!")
        self.other = User.objects.create_user("other", password="pw12345!")
        self.unit = Unit.objects.create(number="101", square_feet=700, monthly_rent=1200)
        Lease.objects.create(
            tenant=self.tenant, unit=self.unit,
            start_date=date(2026, 1, 1), end_date=date(2026, 12, 31), monthly_rent=1200,
        )
        self.form_data = {
            "title": "Leaky sink",
            "category": "plumbing",
            "priority": "urgent",
            "description": "Water under the kitchen sink.",
        }


class MaintenanceModelTests(MaintenanceTestCase):
    def test_new_request_defaults_to_open(self):
        req = MaintenanceRequest.objects.create(
            tenant=self.tenant, unit=self.unit, title="Light out", description="Hallway"
        )
        self.assertEqual(req.status, MaintenanceRequest.Status.OPEN)
        self.assertEqual(req.priority, MaintenanceRequest.Priority.NORMAL)

    def test_str_includes_title_and_unit(self):
        req = MaintenanceRequest.objects.create(
            tenant=self.tenant, unit=self.unit, title="Light out", description="Hallway"
        )
        self.assertEqual(str(req), "Light out (Unit 101)")


class MaintenanceViewTests(MaintenanceTestCase):
    def test_list_requires_login(self):
        response = self.client.get(reverse("maintenance:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_new_request_requires_login(self):
        response = self.client.get(reverse("maintenance:new"))
        self.assertEqual(response.status_code, 302)

    def test_tenant_with_lease_can_open_form(self):
        self.client.login(username="tenant", password="pw12345!")
        response = self.client.get(reverse("maintenance:new"))
        self.assertEqual(response.status_code, 200)

    def test_user_without_lease_is_redirected_from_form(self):
        self.client.login(username="other", password="pw12345!")
        response = self.client.get(reverse("maintenance:new"))
        self.assertRedirects(response, reverse("leases:my_lease"))

    def test_submitting_creates_request_for_tenant_and_unit(self):
        self.client.login(username="tenant", password="pw12345!")
        response = self.client.post(reverse("maintenance:new"), self.form_data)
        self.assertRedirects(response, reverse("maintenance:list"))
        req = MaintenanceRequest.objects.get()
        self.assertEqual(req.tenant, self.tenant)
        self.assertEqual(req.unit, self.unit)
        self.assertEqual(req.status, MaintenanceRequest.Status.OPEN)

    def test_invalid_submission_shows_errors_and_saves_nothing(self):
        self.client.login(username="tenant", password="pw12345!")
        response = self.client.post(reverse("maintenance:new"), {**self.form_data, "title": ""})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(MaintenanceRequest.objects.count(), 0)

    def test_tenant_sees_own_requests_only(self):
        MaintenanceRequest.objects.create(
            tenant=self.tenant, unit=self.unit, title="Mine", description="x"
        )
        self.client.login(username="other", password="pw12345!")
        response = self.client.get(reverse("maintenance:list"))
        self.assertNotContains(response, "Mine")
        self.client.login(username="tenant", password="pw12345!")
        response = self.client.get(reverse("maintenance:list"))
        self.assertContains(response, "Mine")    


        #Announcements

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from announcements.models import Announcement

User = get_user_model()


class AnnouncementTestCase(TestCase):
    def setUp(self):
        self.resident = User.objects.create_user("resident", password="pw12345!")
        self.staff = User.objects.create_user("staff", password="pw12345!", is_staff=True)


class AnnouncementModelTests(AnnouncementTestCase):
    def test_str_is_the_title(self):
        a = Announcement.objects.create(title="Water off", body="Tuesday 9am")
        self.assertEqual(str(a), "Water off")

    def test_new_announcement_is_published_and_not_pinned(self):
        a = Announcement.objects.create(title="Hello", body="x")
        self.assertTrue(a.is_published)
        self.assertFalse(a.is_pinned)


class AnnouncementListTests(AnnouncementTestCase):
    def test_list_requires_login(self):
        response = self.client.get(reverse("announcements:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_unpublished_announcements_are_hidden(self):
        Announcement.objects.create(title="Visible", body="x")
        Announcement.objects.create(title="Secret draft", body="x", is_published=False)
        self.client.login(username="resident", password="pw12345!")
        response = self.client.get(reverse("announcements:list"))
        self.assertContains(response, "Visible")
        self.assertNotContains(response, "Secret draft")

    def test_pinned_announcements_come_first(self):
        Announcement.objects.create(title="Older pinned", body="x", is_pinned=True)
        Announcement.objects.create(title="Newer normal", body="x")
        self.client.login(username="resident", password="pw12345!")
        content = self.client.get(reverse("announcements:list")).content.decode()
        self.assertLess(content.index("Older pinned"), content.index("Newer normal"))

    




    

 