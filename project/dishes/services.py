from django.db.models import F

from .models import TechnologicalMapComposition
from contracts.services.services import get_product_cost


def get_dish_composition(dish, grams=100):
    """
    Получить состав блюда
    """
    tm = dish.get_actual_technological_map()
    tmc = TechnologicalMapComposition.objects.filter(technological_map=tm).annotate(
        volume_per_portion=F('volume') / 100 * grams)
    for el in tmc:
        try:
            el.cost = float(get_product_cost(el.product)) / 1000 * float(el.volume_per_portion)
        except Exception as e:
            el.cost = 0
    return tmc

def get_cost_of_dish(dish, grams=100, ignore_zero_cost=False):
    try:
        composition = get_dish_composition(dish, grams)
        cost = 0
        for element in composition:
            # get_cost_of_product считает стоимость за килограм,
            # поэтому делим на 1000 и умножаем на объём в порции по ТК
            if get_product_cost(element.product):
                cost += float(get_product_cost(element.product)) / 1000 * float(element.volume_per_portion)
            else:
                return 0
        return cost
    except Exception as e:
        print(e)
        return 0