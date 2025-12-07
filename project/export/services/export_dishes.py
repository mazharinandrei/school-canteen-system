import os

from django.utils.timezone import localdate

from dishes.models import Dish, FoodCategory
from .export_to_table.work_with_tables import insert_row, with_workbook


def generate_dishes_file():  # TODO сделать проверку на наличие файла
    file_name = f"export\exported_files\dishes\{localdate()}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)
    result = []

    if os.path.exists(file_path):
        return file_path

    for dish in Dish.objects.all().order_by("category").values():

        category = FoodCategory.objects.filter(id=dish["category_id"]).first().name
        result.append({"name": dish["name"], "category": category})

    return create_dishes_file(result, file_path)


@with_workbook
def create_dishes_file(ws, dishes, file_path):  # TODO: бжу

    insert_row(ws=ws, data=("Категория блюд", "Блюдо"), widths=(20, 75))
    i = 2
    for dish in dishes:
        insert_row(ws, row_index=i, data=(dish["category"], dish["name"]))
        i += 1

    return file_path
