from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from contracts.models import Contract, Counterparty, ContractComposition
from dishes.models import (
    Product,
    Dish,
    FoodCategory,
    TechnologicalMap,
    TechnologicalMapComposition,
)
from main.models import (
    MenuRequirement,
    StudentFeedingCategory,
    MenuRequirementComposition,
    MealType,
)
from staff.models import Staff, Positions
from warehouse.exceptions import NotEnoughProductToWriteOff
from warehouse.models import (
    Warehouse,
    Acceptance,
    Availability,
    WriteOff,
    WriteOffCause,
    ProductTransfer,
)
from warehouse.services.warehouse_transactions import cook_menu


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


class TestWarehouseTransactions(TestCase):
    def setUp(self):
        position = Positions.objects.create(name="position")
        self.staff = Staff.objects.create(
            surname="surname", name="staff", position=position
        )
        student_feeding_category = StudentFeedingCategory.objects.create(
            name="student_feeding_category"
        )
        self.menu = MenuRequirement.objects.create(
            date="2024-03-04",
            student_feeding_category=student_feeding_category,
            students_number=10,
        )
        self.meal_type = MealType.objects.create(name="meal_type")
        self.product = Product.objects.create(name="product1")
        food_category = FoodCategory.objects.create(name="food_category")
        self.dish = Dish.objects.create(category=food_category, name="няяяяя")
        tm = TechnologicalMap.objects.create(
            date="2024-04-03",
            dish=self.dish,
            calories=1,
            proteins=1,
            fats=1,
            carbohydrates=1,
            recipe="...",
        )

        TechnologicalMapComposition.objects.create(
            technological_map=tm,
            product=self.product,
            volume=100,
        )

    def test_cook_empty_menu(self):
        cook_menu(created_by=self.staff, menu=self.menu)
        self.assertEqual(WriteOff.objects.count(), 0)

    def test_cook_menu_not_enough_product(self):
        MenuRequirementComposition.objects.create(
            menu_requirement=self.menu,
            meal_type=self.meal_type,
            dish=self.dish,
            volume_per_student=100,
        )
        Availability.objects.all().delete()
        with self.assertRaises(
            NotEnoughProductToWriteOff,
            msg=f"The product {self.product} must not be enough to be written off",
        ):
            cook_menu(created_by=self.staff, menu=self.menu)

    def test_cook_menu(self):
        warehouse = Warehouse.objects.create(name="Кухня")
        Availability.objects.create(warehouse=warehouse, product=self.product, volume=1)
        MenuRequirementComposition.objects.create(
            menu_requirement=self.menu,
            meal_type=self.meal_type,
            dish=self.dish,
            volume_per_student=100,
        )
        cook_menu(created_by=self.staff, menu=self.menu)
        self.assertEqual(
            first=WriteOff.objects.filter(
                warehouse=warehouse, product=self.product, volume=1
            ).count(),
            second=1,
            msg="There must be only one write-off",
        )
        self.assertEqual(
            self.menu.is_cooked,
            True,
            msg="The menu must be marked as cooked",
        )
