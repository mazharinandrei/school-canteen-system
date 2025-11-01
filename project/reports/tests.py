from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from contracts.models import Contract, Counterparty, ContractComposition
from contracts.services.services import get_product_cost, get_actual_product_costs
from dishes.models import (
    Product,
    Dish,
    FoodCategory,
    TechnologicalMap,
    TechnologicalMapComposition,
)
from staff.models import Staff, Positions


class DishesCostTestCase(TestCase):
    def setUp(self):
        """
        создаётся три договора для продукта, где продукт стоит:
         - 1 р за 1 кг,
         - 20 р за 20 кг,
         - 300 р за 3 кг.
         в среднем должно получиться 2 р за кг
        """
        self.product = Product.objects.create(name="product1")

        position = Positions.objects.create(name="position")

        staff = Staff.objects.create(
            surname="surname", name="surname", position=position
        )

        counterparty = Counterparty.objects.create(
            name="counterparty", address="address1", INN=111111111111, KPP=111111111
        )

        contract1 = Contract.objects.create(
            date="2024-04-03", staff=staff, counterparty=counterparty
        )
        contract2 = Contract.objects.create(
            date="2024-04-03", staff=staff, counterparty=counterparty
        )
        contract3 = Contract.objects.create(
            date="2024-04-03", staff=staff, counterparty=counterparty
        )

        ContractComposition.objects.create(
            contract=contract1,
            product=self.product,
            total_volume=1,
            cost=1,
        )

        ContractComposition.objects.create(
            contract=contract2,
            product=self.product,
            total_volume=10,
            cost=20,
        )

        ContractComposition.objects.create(
            contract=contract3,
            product=self.product,
            total_volume=100,
            cost=300,
        )

    def test_get_product_cost(self):
        self.assertEqual(get_product_cost(self.product), 2)

    def test_get_actual_product_costs(self):
        self.assertEqual(get_actual_product_costs()[0].avg_cost, 2)

    def test_render_costs_of_dishes_report(self):
        """
        создаём ТТК блюда, полностью состоящего из product1.
        цена высчитывается за 100 грамм,
        следовательно, на странице должна быть выведена стоимость 0,20 ₽
        """
        food_category = FoodCategory.objects.create(name="food_category")
        dish = Dish.objects.create(category=food_category, name="няяяяя")
        tm = TechnologicalMap.objects.create(
            date="2024-04-03",
            dish=dish,
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

        User.objects.create_user(username="testuser", password="password123")

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        url = reverse("reports:cost_of_dishes_report")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, dish.name)
        self.assertContains(
            response,
            f"{self.product.name} (100,00 гр.) - 0,20 ₽",
        )
        self.assertContains(
            response,
            f"{dish} - 0,20 ₽",
        )
