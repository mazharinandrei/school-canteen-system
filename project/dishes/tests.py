from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from dishes.models import (
    Product,
    Dish,
    FoodCategory,
    TechnologicalMap,
    TechnologicalMapComposition,
)


class TestTechnologicalMapPages(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )
        self.product1 = Product.objects.create(name="product1")
        self.product2 = Product.objects.create(name="product2")
        self.product3 = Product.objects.create(name="product3")

        self.food_category = FoodCategory.objects.create(name="category")
        self.dish = Dish.objects.create(name="dish", category=self.food_category)

        self.technological_map = TechnologicalMap.objects.create(
            date="2020-02-02",
            dish=self.dish,
            calories=1,
            proteins=1,
            fats=1,
            carbohydrates=1,
            recipe="...",
        )
        self.technological_map_composition = (
            TechnologicalMapComposition.objects.bulk_create(
                (
                    TechnologicalMapComposition(
                        technological_map=self.technological_map,
                        product=self.product1,
                        volume=1,
                    ),
                    TechnologicalMapComposition(
                        technological_map=self.technological_map,
                        product=self.product2,
                        volume=1,
                    ),
                    TechnologicalMapComposition(
                        technological_map=self.technological_map,
                        product=self.product3,
                        volume=1,
                    ),
                )
            )
        )

    def test_get_technological_map(self):
        """
        проверим работу страницы с ТТК
        """
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_technologicalmap")
        )

        url = reverse(
            "dishes:technological_map_by_tm_id", args=[self.technological_map.pk]
        )

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text=str(self.technological_map), status_code=200)

        self.assertContains(response, text=self.dish.name, status_code=200)

        self.assertContains(response, text=self.product1.name, status_code=200)
        self.assertContains(response, text=self.product2.name, status_code=200)
        self.assertContains(response, text=self.product3.name, status_code=200)

    def test_tm_on_all_dishes_page(self):
        """
        проверим отображение ТТК на страницы с блюдами по категориям
        """

        self.user.user_permissions.add(
            Permission.objects.get(codename="view_foodcategory")
        )

        url = reverse("dishes:all")

        self.client = Client()
        self.client.login(username="testuser", password="password123")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            text="ТТК от 2 февраля 2020 г.",
            status_code=200,
        )
