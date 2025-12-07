from ..models import (
    MenuRequirementComposition,
    CycleMenu,
    MealType,
    CycleMenuComposition,
)
from dishes.services import get_dish_composition


from contracts.services.services import get_product_cost


def get_menu_product_composition(menu):
    """
    Получить список продуктов использующихся в меню
    """
    result = []
    menu_product_composition = {}
    menu_composition = MenuRequirementComposition.objects.filter(menu_requirement=menu)
    for element in menu_composition:
        if get_dish_composition(element.dish, element.volume_per_student):

            for el in get_dish_composition(element.dish, element.volume_per_student):
                if (
                    el.product in menu_product_composition.keys()
                ):  # Если продукт уже был в другом блюде
                    menu_product_composition[el.product] += (
                        float(el.volume_per_portion) * menu.students_number
                    )
                else:
                    menu_product_composition[el.product] = (
                        float(el.volume_per_portion) * menu.students_number
                    )
        else:
            raise Exception(f"No composition {element.dish}")

    for key, value in menu_product_composition.items():
        try:
            cost = get_product_cost(key) / 1000 * value

        except Exception:
            cost = None

        result.append({"product": key, "volume": value, "cost": cost})

    return result


def get_menu_nutrients(menu):
    """
    Получить БЖУ меню
    """
    result = {"calories": 0, "proteins": 0, "fats": 0, "carbohydrates": 0}
    menu_composition = MenuRequirementComposition.objects.filter(menu_requirement=menu)
    no_tm = []
    for element in menu_composition:
        try:
            tm = element.dish.technological_maps.actual()

            result["calories"] += tm.calories
            result["proteins"] += tm.proteins
            result["fats"] += tm.fats
            result["carbohydrates"] += tm.carbohydrates

        except AttributeError:
            no_tm.append(element.dish)

    return result, no_tm


def get_cycle_menu_day_composition(week_number, week_day, student_feeding_category):
    result = []
    for meal_type in MealType.objects.all():
        try:
            cycle_menu = CycleMenu.objects.filter(
                week_number=week_number,
                week_day=week_day,
                student_feeding_category=student_feeding_category,
                meal_type=meal_type,
            ).latest("actual_since")

            dishes = CycleMenuComposition.objects.filter(cycle_menu_day=cycle_menu)
            result.append({"meal_type": meal_type, "dishes": dishes})
        except Exception:

            pass

    return result
