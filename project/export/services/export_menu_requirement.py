import os

from main.services.menu_info import get_menu_product_composition

from ..services.export_menu import (
    insert_menu_data,
    get_name_of_category,
    get_menu_data,
    get_menu,
)
from .export_to_table.work_with_tables import insert_row, with_workbook, center_aligment


def generate_menu_requirement_file(date, student_feeding_category):
    menu_requirement = get_menu(date, student_feeding_category)
    name_of_category = get_name_of_category(student_feeding_category)
    file_name = (
        f"export\exported_files\menu-requirement\Меню {name_of_category} {date}.xlsx"
    )
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    data = get_menu_data(date, student_feeding_category)

    data["product_composition"] = get_menu_product_composition(menu_requirement)

    return create_menu_requirement_file(data=data, file_path=file_path)


@with_workbook
def create_menu_requirement_file(ws, data, file_path):

    i = insert_menu_data(ws=ws, data=data)

    insert_row(
        ws=ws, row_index=i, data=("Необходимые продукты",), alignment=center_aligment()
    )
    ws.merge_cells(f"A{i}:F{i}")
    i += 1

    insert_row(
        ws=ws,
        row_index=i,
        data=("Наименование продукта", "Количество, г", "Стоимость, ₽"),
    )
    i += 1

    for el in data["product_composition"]:
        if el["cost"] is not None:
            cost = el["cost"]
        else:
            cost = ""
        insert_row(
            ws=ws, row_index=i, data=("", el["product"].name, el["volume"], cost)
        )
        i += 1
    return file_path
