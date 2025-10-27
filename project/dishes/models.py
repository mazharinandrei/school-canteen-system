from django.db import models
from django.urls import reverse_lazy
from django.utils.timezone import localdate


# Create your models here.


class FoodCategory(models.Model):  # TODO: добавить slug
    name = models.CharField(verbose_name="Название категории блюд", max_length=100)

    class Meta:
        verbose_name = "Категория блюд"
        verbose_name_plural = "Категории блюд"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse_lazy("dishes:food_category", args=[self.pk])


# Конкретное блюдо
class Dish(models.Model):
    name = models.CharField("Название блюда", max_length=100, blank=False)

    category = models.ForeignKey(
        FoodCategory,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name="Категория",
        related_name="dishes",
    )

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"

    def list_technological_maps(self):
        return TechnologicalMap.objects.filter(dish=self.id)

    def get_actual_technological_map(self):
        try:
            return TechnologicalMap.objects.filter(
                dish=self.id, date__lte=localdate()
            ).latest("date")
        except Exception:
            return None

    def get_nutrients(self, volume=200):
        """
        Получить БЖУ блюда

        Если у блюда нет ТК, то возвращаются нули

            :return: (calories, proteins, fats, carbohydrates)
        """
        try:
            tm = self.get_actual_technological_map()
            return (
                tm.calories / 100 * volume,
                tm.proteins / 100 * volume,
                tm.fats / 100 * volume,
                tm.carbohydrates / 100 * volume,
            )
        except Exception:
            return 0, 0, 0, 0

    def __str__(self):
        return self.name


# Продукт
class Product(models.Model):
    name = models.CharField("Название продукта", max_length=20, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"


class TechnologicalMap(models.Model):
    date = models.DateField(verbose_name="ТТК актуально с даты")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT)
    calories = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # TODO: validators = []
    proteins = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # TODO: validators = []
    fats = models.DecimalField(max_digits=5, decimal_places=2)  # TODO: validators = []
    carbohydrates = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # TODO: validators = []
    recipe = models.TextField()
    products = models.ManyToManyField(
        Product,
        through="TechnologicalMapComposition",
        through_fields=("technological_map", "product"),
    )

    def get_absolute_url(self):
        return reverse_lazy("dishes:technological_map_by_tm_id", args=[self.pk])

    def get_composition(self):
        try:
            tmc = TechnologicalMapComposition.objects.filter(technological_map=self.id)
            data2 = []
            for i in tmc:
                data2.append((i.product, i.volume))
            return data2
        except Product.DoesNotExist:
            return "ТТК не найдено!"  # TODO: неправильно!

    def __str__(self):
        return f"ТТК {self.dish} от {self.date}"

    class Meta:
        ordering = ["-date"]
        verbose_name = "Технологическая карта"
        verbose_name_plural = "Технологические карты"


class TechnologicalMapComposition(models.Model):
    technological_map = models.ForeignKey(
        TechnologicalMap, on_delete=models.PROTECT, related_name="composition"
    )

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    volume = models.DecimalField(max_digits=5, decimal_places=2)

    # TODO: единица измерения
    def __str__(self):
        return f"Состав {self.technological_map}"

    class Meta:
        verbose_name = "Состав технологической карты"
        verbose_name_plural = "Составы технологической карты"


def get_dishes_with_no_tc():
    return Dish.objects.exclude(id__in=TechnologicalMap.objects.values("dish"))
