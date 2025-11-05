from decimal import Decimal

from django.db import models
from django.db.models import ExpressionWrapper, F, IntegerField, FloatField
from django.urls import reverse

from staff.models import Staff

from dishes.models import Product


class Counterparty(models.Model):  # Контрагенты
    name = models.CharField("Наименование организации", max_length=300)
    address = models.CharField("Адрес", max_length=300)
    INN = models.CharField("ИНН", max_length=12)
    KPP = models.CharField("КПП", max_length=9)

    note = models.TextField(blank=True, null=True)  # Поле для примечаний

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("contracts:render_counterparty", args=[self.pk])

    class Meta:
        verbose_name = "Контрагент"
        verbose_name_plural = "Контрагенты"


class Contract(models.Model):
    date = models.DateField(verbose_name="Дата договора")

    staff = models.ForeignKey(
        Staff,
        verbose_name="Ответственный сотрудник",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        default=2,
    )

    counterparty = models.ForeignKey(
        Counterparty,
        verbose_name="Организация",
        on_delete=models.PROTECT,
        related_name="contracts",
    )

    is_actual = models.BooleanField(
        verbose_name="Актуальность", blank=True, null=True, default=True
    )

    file = models.FileField(
        verbose_name="Файл договора",
        upload_to="contracts/contracts_files",
        blank=True,
        null=True,
    )
    products = models.ManyToManyField(
        Product,
        verbose_name="Продукты",
        through="ContractComposition",
        through_fields=("contract", "product"),
    )

    note = models.TextField(verbose_name="Примечание", blank=True, null=True)

    def __str__(self):
        return f"Договор с {self.counterparty} от {self.date}"

    def get_composition(self):
        return self.composition.annotate(
            received_percent=ExpressionWrapper(
                (F("received_volume") * 100) / F("total_volume"),
                output_field=IntegerField(),
            ),
            unit_price=ExpressionWrapper(
                F("cost") / F("total_volume"), output_field=FloatField()
            ),
        )

    def get_absolute_url(self):
        return reverse("contracts:render_contract", args=[self.pk])

    class Meta:
        ordering = ["-date"]
        verbose_name = "Договор"
        verbose_name_plural = "Договора"


class ContractComposition(models.Model):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.PROTECT,
        verbose_name="Договор",
        related_name="composition",
    )

    product = models.ForeignKey(
        Product, verbose_name="Продукт", on_delete=models.PROTECT
    )

    total_volume = models.DecimalField(
        verbose_name="Количество по договору, кг", max_digits=15, decimal_places=3
    )

    received_volume = models.DecimalField(
        verbose_name="Принято, кг", max_digits=15, decimal_places=3, default=Decimal(0)
    )
    cost = models.DecimalField(
        verbose_name="Полная стоимость", max_digits=15, decimal_places=2
    )

    def __str__(self):
        return f"{self.contract}: {self.product} - {self.received_volume}/{self.total_volume}"

    class Meta:
        verbose_name = "Состав договора"
        verbose_name_plural = "Составы договоров"
