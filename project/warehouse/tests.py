from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from contracts.models import Contract, Counterparty, ContractComposition
from dishes.models import Product
from staff.models import Staff, Positions
from warehouse.models import (
    Warehouse,
    Acceptance,
    Availability,
    WriteOff,
    WriteOffCause,
    ProductTransfer,
)


class TestWarehousePages(TestCase):
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

        self.warehouse = Warehouse.objects.create(name="warehouse", address="address2")

    def test_list_acceptance(self):
        """проверим отображение списка приёмов на склад"""
        acceptance = Acceptance.objects.create(
            warehouse=self.warehouse,
            contract=self.contract,
            product=self.product,
            volume=100,
            staff=self.staff,
        )

        url = reverse("warehouse:acceptance")

        self.user.user_permissions.add(
            Permission.objects.get(codename="view_acceptance")
        )

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text=acceptance.warehouse.name, status_code=200)

        self.assertContains(response, text=acceptance.product.name, status_code=200)

        self.assertContains(response, text=acceptance.staff.name, status_code=200)

    def test_list_availability(self):
        """проверим отображение наличия на складе"""
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_availability")
        )

        availability = Availability.objects.create(
            warehouse=self.warehouse, product=self.product, volume=100
        )

        url = reverse("warehouse:availability")

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text=availability.warehouse.name, status_code=200)

        self.assertContains(response, text=availability.product.name, status_code=200)

    def test_list_write_off(self):
        """проверим отображение списка списаний со склада"""
        self.user.user_permissions.add(Permission.objects.get(codename="view_writeoff"))

        writeoff_cause = WriteOffCause.objects.create(name="writeoff_cause")

        writeoff = WriteOff.objects.create(
            staff=self.staff,
            warehouse=self.warehouse,
            product=self.product,
            volume=100,
            cause=writeoff_cause,
        )

        url = reverse("warehouse:write_off")

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text=writeoff.warehouse.name, status_code=200)

        self.assertContains(response, text=writeoff.product.name, status_code=200)

    def test_list_product_transfer(self):
        """проверим отображение списка перемещений со склада"""
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_producttransfer")
        )

        product_transfer = ProductTransfer.objects.create(
            staff=self.staff,
            warehouse_from=self.warehouse,
            warehouse_to=self.warehouse,
            product=self.product,
            volume=100,
        )

        url = reverse("warehouse:transfers")

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response, text=product_transfer.warehouse_to.name, status_code=200
        )

        self.assertContains(
            response, text=product_transfer.warehouse_from.name, status_code=200
        )

        self.assertContains(
            response, text=product_transfer.product.name, status_code=200
        )
