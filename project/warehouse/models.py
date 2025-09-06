from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from dishes.models import Product


# Create your models here.

class Warehouse(models.Model):  # Склад
    name = models.CharField("Наименование склада", max_length=100)
    address = models.CharField("Адрес склада", max_length=100)
    note = models.TextField(blank=True, null=True)  # Поле для примечаний и контактных данных

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'


class Acceptance(models.Model):  # Приём на склад
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    contract = models.ForeignKey("contracts.Contract", on_delete=models.PROTECT, verbose_name="На основании договора")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    volume = models.DecimalField("Объём",
                                 max_digits=9, decimal_places=3,
                                 validators=[
                                     MinValueValidator(0.1)
                                 ])
    datetime = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey("staff.Staff", verbose_name="Ответственный", on_delete=models.PROTECT, blank=True,
                              null=True, default=2)
    note = models.TextField(blank=True, null=True)  # Поле для примечаний

    # TODO: единица измерения

    def __str__(self):
        return f"Приём на склад {self.warehouse}: {self.product}, {self.volume}"

    class Meta:
        verbose_name = 'Приём на склад'
        verbose_name_plural = 'Приёмы на склады'


class WriteOffCause(models.Model):
    name = models.CharField("Наименование причины списания", max_length=100)

    def __str__(self):
        return self.name


class WriteOff(models.Model):  # Списание со склада
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    volume = models.DecimalField("Объём",
                                 max_digits=9,
                                 decimal_places=3,
                                 validators=[
                                     MinValueValidator(0.1),
                                 ])
    datetime = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey("staff.Staff", verbose_name="Ответственный", on_delete=models.PROTECT, blank=True,
                              null=True, default=2)
    cause = models.ForeignKey(WriteOffCause, on_delete=models.PROTECT)
    note = models.TextField(blank=True, null=True)  # Поле для примечаний

    def __str__(self):
        return f"Списание co склада {self.warehouse}: {self.product}, {self.volume}"

    class Meta:
        verbose_name = 'Списание co склада'
        verbose_name_plural = 'Списания co складов'


class ProductTransfer(models.Model):  # Перевод товара между складами
    warehouse_from = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='warehouse_from',
                                       verbose_name="Со склада")
    warehouse_to = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='warehouse_to',
                                     verbose_name="На склад")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    volume = models.DecimalField("Объём",
                                 max_digits=9,
                                 decimal_places=3,
                                 validators=[
                                     MinValueValidator(0.1),
                                 ])
    datetime = models.DateTimeField(auto_now_add=True)
    staff = models.ForeignKey("staff.Staff", on_delete=models.PROTECT, verbose_name="Ответственный", blank=True,
                              null=True, default=2)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Перевод товара со склада {self.warehouse_from} на склад {self.warehouse_to}: {self.product}, {self.volume}"


class Availability(models.Model):  # Наличие на складе
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    volume = models.DecimalField("Объём",
                                 max_digits=9,
                                 decimal_places=3,
                                 validators=[
                                     MinValueValidator(0.1),
                                 ],
                                 default=0)

    def __str__(self):
        return f"Наличие на складе {self.warehouse}: {self.product}, {self.volume}"

    class Meta:
        verbose_name = 'Наличие на складе'
        verbose_name_plural = 'Наличие на складе'


class FactAvailability(models.Model):  # Фактическое наличие на складе
    datetime = models.DateTimeField(auto_now_add=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    volume = models.DecimalField("Объём",
                                 max_digits=9,
                                 decimal_places=3,
                                 validators=[
                                     MinValueValidator(0.1),
                                 ],
                                 default=0)

    def __str__(self):
        return f"Фактическое наличие на складе {self.warehouse}: {self.product}, {self.volume} {self.datetime}"

    class Meta:
        verbose_name = 'Фактическое наличие на складе'
        verbose_name_plural = 'Фактическое наличие на складе'


class ProductLimit(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name="Склад")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="Продукт")
    min_volume = models.IntegerField(verbose_name="Объём минимального запаса")

    def __str__(self):
        return f"Лимит продукта {self.product} на сладе {self.warehouse}"

    class Meta:
        verbose_name = 'Лимит продукта на складе'
        verbose_name_plural = 'Лимиты продуктов на складе'
