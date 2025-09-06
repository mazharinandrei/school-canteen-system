from decimal import Decimal, InvalidOperation

from django.db import models
from django.db.models import Avg, ExpressionWrapper, F, IntegerField, FloatField

from staff.models import Staff

from dishes.models import Product


# Create your models here.

class Counterparty(models.Model):  # Контрагенты
    name = models.CharField('Наименование организации',
                            max_length=300)
    address = models.CharField('Адрес',
                               max_length=300)
    INN = models.CharField('ИНН',
                           max_length=12)
    KPP = models.CharField('КПП',
                           max_length=9)

    note = models.TextField(blank=True, null=True)  # Поле для примечаний

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Контрагент'
        verbose_name_plural = 'Контрагенты'


class Contract(models.Model):
    date = models.DateField()
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT, blank=True, null=True, default=2)
    counterparty = models.ForeignKey(Counterparty, on_delete=models.PROTECT)
    is_actual = models.BooleanField(blank=True, null=True, default=True)
    file = models.FileField(upload_to='contracts/contracts_files', blank=True, null=True)
    products = models.ManyToManyField(
        Product,
        through="ContractComposition",
        through_fields=("contract", "product")
    )
    note = models.TextField(blank=True, null=True)  # Поле для примечаний

    def __str__(self):
        return f"Договор с {self.counterparty} от {self.date}"

    def get_composition(self):
        return ContractComposition.objects.filter(contract=self).annotate(
            received_percent=ExpressionWrapper(
                (F("received_volume") * 100) / F("total_volume"),
                output_field=IntegerField()
            ),
            unit_price=ExpressionWrapper(
                F("cost") / F("total_volume"),
                output_field=FloatField()
            )
        )

    class Meta:
        verbose_name = 'Договор'
        verbose_name_plural = 'Договора'


class ContractComposition(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    total_volume = models.DecimalField(max_digits=15, decimal_places=3)
    received_volume = models.DecimalField(max_digits=15, decimal_places=3, default=Decimal(0))
    cost = models.DecimalField(max_digits=15, decimal_places=2)

    def __str__(self):
        return f"{self.contract}: {self.product} - {self.received_volume}/{self.total_volume}"

    class Meta:
        verbose_name = 'Состав договора'
        verbose_name_plural = 'Составы договоров'


def get_cost_of_product(product):
    actual_contracts = Contract.objects.filter(is_actual=True)

    # Получаем средние значения стоимости и объема для актуальных контрактов
    avg_data = ContractComposition.objects.filter(product=product.id, contract__in=actual_contracts) \
        .aggregate(avg_cost=Avg("cost"), avg_volume=Avg("total_volume"))

    cost = avg_data.get("avg_cost")
    volume = avg_data.get("avg_volume")

    # Если данные найдены, считаем среднюю стоимость за кг
    if cost is not None and volume not in [None, 0]:
        try:
            return Decimal(cost) / Decimal(volume)
        except (InvalidOperation, ZeroDivisionError):
            return None

    # Если актуальных контрактов нет, ищем данные среди всех записей
    avg_data = ContractComposition.objects.filter(product=product.id) \
        .aggregate(avg_cost=Avg("cost"), avg_volume=Avg("total_volume"))

    cost = avg_data.get("avg_cost")
    volume = avg_data.get("avg_volume")

    if cost is not None and volume not in [None, 0]:
        try:
            return Decimal(cost) / Decimal(volume)
        except (InvalidOperation, ZeroDivisionError):
            return None

    return None
