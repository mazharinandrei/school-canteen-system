from django.db.models import Avg, Q, F

from dishes.models import Product


def get_actual_product_costs():
    return Product.objects.annotate(
        avg_cost=Avg(
            F("contractcomposition__cost") / F("contractcomposition__total_volume"),
            filter=Q(contractcomposition__contract__is_actual=True),
        )
    )


def get_product_cost(product):
    if (
        product_in_actual_prices := get_actual_product_costs()
        .filter(contractcomposition__product=product)
        .first()
    ):
        return product_in_actual_prices.avg_cost
    return None
