from collections import defaultdict

from django.db.models import Avg, Q

from ..models import Contract
from dishes.models import Product


def get_actual_product_costs():
    return Product.objects.annotate(
        avg_cost=Avg(
            "contractcomposition__cost",
            filter=Q(contractcomposition__contract__is_actual=True),
        )
    )


def get_actual_contracts():
    actual_contracts = Contract.objects.filter(is_actual=True)
    return actual_contracts


def get_actual_avg_price_of_all_products():
    abchihba = []

    for contract in get_actual_contracts():
        for el in contract.get_composition():
            abchihba.append(
                {
                    "product": el.product,
                    "unit_price": el.unit_price,
                }
            )

    # Словарь для хранения суммы цен и количества записей
    product_prices = defaultdict(lambda: {"total_price": 0, "count": 0})

    # Заполняем данные
    for entry in abchihba:
        product = entry["product"]
        product_prices[product]["total_price"] += entry["unit_price"]
        product_prices[product]["count"] += 1

    # Вычисляем среднюю цену
    result = [
        {"product": product, "avg_kilo_price": total["total_price"] / total["count"]}
        for product, total in product_prices.items()
    ]
    return result


def get_product_cost(product):
    avg_prices_of_all_products = get_actual_avg_price_of_all_products()
    for item in avg_prices_of_all_products:
        if item["product"] == product:

            return item["avg_kilo_price"]
    return None
