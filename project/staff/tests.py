from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from contracts.models import Contract, Counterparty, ContractComposition
from dishes.models import Product
from staff.models import Positions, Staff


class TestStaffPages(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.position = Positions.objects.create(name="Pirate")
        self.staff = Staff.objects.create(
            surname="Threepwood", name="Guybrush", position=self.position
        )

    def test_staff_detail_without_permission(self):
        url = reverse("staff:render_staff", args=[self.staff.pk])
        self.client = Client()
        self.client.login(username="testuser", password="password123")
        response = self.client.get(url)

        self.assertEqual(
            response.status_code, 403, msg="You can't view staff without permission"
        )

    def test_staff_detail(self):
        counterparty = Counterparty.objects.create(
            name="counterparty", address="address1", INN=111111111111, KPP=111111111
        )
        contract = Contract.objects.create(
            date="2009-07-15", staff=self.staff, counterparty=counterparty
        )

        ContractComposition.objects.create(
            contract=contract,
            product=Product.objects.create(name="spam"),
            total_volume=1,
            cost=1,
        )

        self.user.user_permissions.add(Permission.objects.get(codename="view_staff"))
        url = reverse("staff:render_staff", args=[self.staff.pk])
        self.client = Client()
        self.client.login(username="testuser", password="password123")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text="Pirate", status_code=200)

        self.assertContains(response, text="G.", status_code=200)
        self.assertContains(response, text="Threepwood", status_code=200)

        self.assertContains(response, text="spam", status_code=200)
