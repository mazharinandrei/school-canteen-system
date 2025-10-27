import os


from .export_to_table.work_with_tables import with_workbook, insert_row, bold_font

from dishes.models import TechnologicalMapComposition, TechnologicalMap


def generate_technological_map_file(technological_map):
    technological_map = TechnologicalMap.objects.get(id=technological_map)
    file_name = f"export\exported_files\\tm\ТТК блюда {technological_map.dish.name} от {technological_map.date}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path
    data = {
        "technological_map": technological_map,
        "technological_map_composition": TechnologicalMapComposition.objects.filter(
            technological_map=technological_map
        ),
    }
    return create_technological_map_file(data=data, file_path=file_path)


@with_workbook
def create_technological_map_file(ws, data, file_path):
    insert_row(ws, data=(data["technological_map"].dish.name,), fonts=(bold_font(),))
    i = 2

    ws.merge_cells(f"A{1}:D{1}")

    insert_row(
        ws,
        row_index=i,
        data=("Калорийность, ккал", "Белки, г", "Жиры, г", "Углеводы, г"),
    )

    i += 1

    insert_row(
        ws,
        row_index=i,
        data=(
            data["technological_map"].calories,
            data["technological_map"].proteins,
            data["technological_map"].fats,
            data["technological_map"].carbohydrates,
        ),
    )

    i += 1

    insert_row(ws, row_index=i, data=("Состав ТТК на 100 г",), fonts=(bold_font(),))
    ws.merge_cells(f"A{i}:D{i}")
    i += 1

    insert_row(ws, row_index=i, data=("Продукт", "Количество, г"))
    i += 1

    for tmc in data["technological_map_composition"]:
        insert_row(ws, row_index=i, data=(tmc.product.name, tmc.volume))
        i += 1

    ws["F1"] = "Технология приготовления"
    ws["F2"] = data["technological_map"].recipe
    return file_path
