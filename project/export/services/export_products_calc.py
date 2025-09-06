import os
from datetime import datetime

from main.services.products_calc import products_calc_by_date_interval

from .export_to_table.work_with_tables import with_workbook, insert_row, center_aligment
from main.models import StudentFeedingCategory


def generate_products_calc_file(start_date, end_date, student_feeding_category, planned_people_number):
    file_name = f"export\exported_files\products-calc\{start_date}-{end_date}-{student_feeding_category}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    products = products_calc_by_date_interval(start_date=start_date,
                                              end_date=end_date,
                                              student_feeding_category=student_feeding_category,
                                              planned_people_number=planned_people_number)
    products_calc_info = {

        "start_date": datetime.strptime(start_date, '%Y-%m-%d').strftime('%d.%m.%Y'),
        "end_date": datetime.strptime(end_date, '%Y-%m-%d').strftime('%d.%m.%Y'),
        "student_feeding_category": StudentFeedingCategory.objects.get(id=student_feeding_category).name,
        "planned_people_number": planned_people_number
    }

    return create_products_calc_file(data=products, products_calc_info=products_calc_info, file_path=file_path)

@with_workbook
def create_products_calc_file(ws, data, products_calc_info, file_path):
    insert_row(ws=ws, row_index=1, data=("Список продуктов на заказ",), alignment=center_aligment())
    ws.merge_cells("A1:B1")
    insert_row(ws=ws, row_index=2, data=("Начало периода", products_calc_info['start_date']))
    insert_row(ws=ws, row_index=3, data=("Конец периода", products_calc_info['end_date']))
    insert_row(ws=ws, row_index=4, data=("Категория питающихся", products_calc_info['student_feeding_category']))
    insert_row(ws=ws, row_index=5, data=("Количество питающихся", products_calc_info['planned_people_number']))
    insert_row(ws=ws,
               row_index=6,
               widths=(25, 20),
               data=("Продукт", "Количество, кг"),
               alignment=center_aligment())
    for product in data:
        insert_row(ws=ws,
                   row_index=data.index(product) + 7,
                   data=(product['product'].name, product['volume']))

    return file_path