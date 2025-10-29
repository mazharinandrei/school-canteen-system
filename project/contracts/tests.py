from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from contracts.models import Counterparty, Contract, ContractComposition
from dishes.models import Product
from staff.models import Positions, Staff


class TestContracts(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.product = Product.objects.create(name="product1")
        self.position = Positions.objects.create(name="position")
        self.staff = Staff.objects.create(
            surname="surname", name="staff", position=self.position
        )

        self.counterparty = Counterparty.objects.create(
            name="counterparty", address="address1", INN=111111111111, KPP=111111111
        )
        self.contract = Contract.objects.create(
            date="2020-02-02", staff=self.staff, counterparty=self.counterparty
        )
        self.contract_composition = ContractComposition.objects.create(
            contract=self.contract,
            product=self.product,
            total_volume=1000,
            cost=1000,
        )

    def test_list_contracts(self):
        """проверим страницу со всеми договорами"""
        self.user.user_permissions.add(Permission.objects.get(codename="view_contract"))

        url = reverse("contracts:all_contracts")

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text=str(self.contract), status_code=200)

        self.assertContains(response, text=self.contract.staff, status_code=200)
        self.assertContains(response, text=self.contract.counterparty, status_code=200)
        self.assertContains(response, text=self.product.name, status_code=200)

    def test_get_contract(self):
        """проверим страницу с договором"""
        self.user.user_permissions.add(Permission.objects.get(codename="view_contract"))

        url = reverse("contracts:render_contract", args=[self.contract.pk])

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text=str(self.contract), status_code=200)

        self.assertContains(response, text=self.contract.staff, status_code=200)
        self.assertContains(response, text=self.contract.counterparty, status_code=200)
        self.assertContains(response, text=self.product.name, status_code=200)
