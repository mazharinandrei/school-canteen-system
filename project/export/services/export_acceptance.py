import os

from django.utils.timezone import localdate

from .export_to_table.work_with_tables import insert_row, with_workbook, center_aligment, bold_font, regular_font
from warehouse.models import Acceptance

def generate_acceptance_file():
    date = localdate()
    file_name = f"export\exported_files\\acceptance\{date}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    acceptance = Acceptance.objects.all()

    return create_acceptance_file(date=date, acceptances=acceptance, file_path=file_path)


@with_workbook
def create_acceptance_file(ws, date, acceptances, file_path):
    insert_row(ws=ws, row_index=1, data=("Приёмы на склады",), alignment=center_aligment(), fonts=(bold_font(),))
    ws.merge_cells("A1:E1")
    insert_row(ws=ws, row_index=2, data=("Дата:", date.strftime('%d.%m.%Y')), fonts=(bold_font(), regular_font()))
    insert_row(ws=ws, row_index=3, data=("Склад", "Принято по договору", "Наименование продукта", "Количество, кг", "Ответственный"),
               fonts=[bold_font() for i in range(5)])
    i = 4
    for acceptance in acceptances:

        insert_row(ws,
                   row_index=i,
                   data=(acceptance.warehouse.name, str(acceptance.contract), acceptance.product.name, acceptance.volume,
                         f"{acceptance.staff.surname} {acceptance.staff.name} {acceptance.staff.second_name}"),
                   widths=(10, 50, 25, 15, 25)
                   )
        i += 1

    return file_path
