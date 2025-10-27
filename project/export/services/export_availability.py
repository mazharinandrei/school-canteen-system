import os

from django.utils.timezone import localdate

from .export_to_table.work_with_tables import (
    insert_row,
    with_workbook,
    center_aligment,
    bold_font,
    regular_font,
)
from warehouse.models import Availability


def generate_availability_file():
    date = localdate()
    file_name = f"export\exported_files\\availability\{date}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    availability = Availability.objects.all()

    return create_acceptance_file(
        date=date, availabilities=availability, file_path=file_path
    )


@with_workbook
def create_acceptance_file(ws, date, availabilities, file_path):
    insert_row(
        ws=ws,
        row_index=1,
        data=("Наличие на складах",),
        alignment=center_aligment(),
        fonts=(bold_font(),),
    )
    ws.merge_cells("A1:C1")
    insert_row(
        ws=ws,
        row_index=2,
        data=("Дата отчёта:", date.strftime("%d.%m.%Y")),
        fonts=(bold_font(), regular_font()),
    )
    insert_row(
        ws=ws,
        row_index=3,
        data=("Склад", "Наименование продукта", "Количество, кг"),
        fonts=[bold_font() for i in range(5)],
    )
    i = 4
    for availability in availabilities:
        insert_row(
            ws,
            row_index=i,
            data=(
                availability.warehouse.name,
                availability.product.name,
                availability.volume,
            ),
            widths=(15, 25, 15),
        )
        i += 1

    return file_path
