import os

from django.utils.timezone import localdate
from warehouse.models import WriteOff

from .export_to_table.work_with_tables import (
    insert_row,
    bold_font,
    regular_font,
    center_aligment,
    with_workbook,
)


def generate_write_off_file():
    date = localdate()
    file_name = f"export\exported_files\\writeoff\{date}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    write_off = WriteOff.objects.all()

    return create_write_off_file(date=date, write_offs=write_off, file_path=file_path)


@with_workbook
def create_write_off_file(ws, date, write_offs, file_path):
    insert_row(
        ws=ws,
        row_index=1,
        data=("Списания со складов",),
        alignment=center_aligment(),
        fonts=(bold_font(),),
    )
    ws.merge_cells("A1:G1")
    insert_row(
        ws=ws,
        row_index=2,
        data=("Дата отчёта:", date.strftime("%d.%m.%Y")),
        fonts=(bold_font(), regular_font()),
    )
    insert_row(
        ws=ws,
        row_index=3,
        data=(
            "Дата и время",
            "Склад",
            "Наименование продукта",
            "Количество, кг",
            "Ответственный",
            "Причина",
            "Примечание",
        ),
        fonts=[bold_font() for i in range(7)],
    )
    i = 4
    for write_off in write_offs:
        if write_off.staff:
            surname = write_off.staff.surname
            name = write_off.staff.name
            second_name = write_off.staff.second_name
        else:
            surname = name = second_name = ""
        insert_row(
            ws,
            row_index=i,
            data=(
                write_off.datetime.strftime("%d.%m.%Y %H:%M"),
                write_off.warehouse.name,
                write_off.product.name,
                write_off.volume,
                f"{surname} {name} {second_name}",
                write_off.cause.name,
                write_off.note,
            ),
            widths=(15, 10, 25, 15, 25, 30, 25),
        )
        i += 1

    return file_path
