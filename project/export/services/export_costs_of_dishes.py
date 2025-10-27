import os

from dishes.models import Dish

from dishes.services import get_cost_of_dish
from django.utils.timezone import localdate

from .export_to_table.work_with_tables import insert_row, with_workbook


def generate_costs_of_dishes_file():
    file_name = f"export\exported_files\costs_of_dishes\{localdate()}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    result = []
    for dish in Dish.objects.all():
        cost = get_cost_of_dish(dish)
        if cost:
            result.append(
                {
                    "dish": dish.name,
                    "cost": str("{:.2f}".format(float(cost))).replace(".", ","),
                }
            )

    return create_costs_of_dishes_file(result, file_path)


@with_workbook
def create_costs_of_dishes_file(ws, data, file_path):
    insert_row(ws=ws, data=("Дата отчёта", localdate()), widths=(50, 15))

    insert_row(ws=ws, row_index=2, data=("Наименование блюда", "Стоимость, руб"))
    i = 3
    for el in data:
        insert_row(ws=ws, row_index=i, data=(el["dish"], el["cost"]))
        i += 1
    return file_path
