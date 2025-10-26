from dishes.models import Dish

from main_project.contracts.models import get_cost_of_product


def get_dishes_without_tm():
    dishes = Dish.objects.all()
    return [dish for dish in dishes if not dish.get_actual_technological_map()]


def is_dish_have_tm(dish):
    if dish.get_actual_technological_map():
        return True
    return False

def get_dishes_with_tm(dish):
    pass

def is_tm_have_cost(tm):
    for product in tm.products:
        if not get_cost_of_product(product):
            return False
    return True


def get_dishes_with_cost():
    dishes = Dish.objects.all()
    result = []
    for dish in dishes:
        tm = dish.get_actual_technological_map()
        if is_tm_have_cost(tm):
            result.append(dish)

    return result


def get_dishes_without_cost():
    return Dish.objects.exclude(get_dishes_with_cost())


