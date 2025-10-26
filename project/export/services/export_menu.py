import os
from datetime import datetime

from .export_to_table.work_with_tables import insert_row, with_workbook, bold_font, center_aligment
from main.models import MenuRequirement, MenuRequirementComposition, MealType, StudentFeedingCategory



def get_name_of_category(student_feeding_category):
    return StudentFeedingCategory.objects.get(id=student_feeding_category).name.split()[1] + " лет"


def get_menu(date, student_feeding_category):
    date = datetime.strptime(date, '%Y-%m-%d').date()
    return MenuRequirement.objects.get(date=date, student_feeding_category=student_feeding_category)


def get_menu_data(date, student_feeding_category):
    name_of_category = get_name_of_category(student_feeding_category)
    menu = get_menu(date, student_feeding_category)

    menu_list = []

    for meal_type in MealType.objects.all():
        meal_type_dict = {"meal_type": meal_type.name, "dishes": []}

        composition = MenuRequirementComposition.objects.filter(menu_requirement=menu, meal_type=meal_type)

        sum_calories = 0
        sum_proteins = 0
        sum_fats = 0
        sum_carbohydrates = 0

        for el in composition:
            nutrients = el.dish.get_nutrients(volume=el.volume_per_student)
            sum_calories += nutrients[0]
            sum_proteins += nutrients[1]
            sum_fats += nutrients[2]
            sum_carbohydrates += nutrients[3]

            meal_type_dict["dishes"].append({
                "dish": el.dish.name,
                "volume_per_student": float(el.volume_per_student),
                "calories": float(nutrients[0]),
                "proteins": float(nutrients[1]),
                "fats": float(nutrients[2]),
                "carbohydrates": float(nutrients[3]),
            })

        meal_type_dict["calories"] = sum_calories
        meal_type_dict["proteins"] = sum_proteins
        meal_type_dict["fats"] = sum_fats
        meal_type_dict["carbohydrates"] = sum_carbohydrates

        menu_list.append(meal_type_dict)

    return {"date": menu.date, "student_feeding_category": name_of_category, "menu": menu_list}


def generate_menu_file(date, student_feeding_category):
    name_of_category = get_name_of_category(student_feeding_category)
    file_name = f"export\exported_files\menu\Меню {name_of_category} {date}.xlsx"
    file_path = os.path.join(os.getcwd(), file_name)

    if os.path.exists(file_path):
        return file_path

    return create_menu_file(data=get_menu_data(date, student_feeding_category))


@with_workbook
def create_menu_file(ws, data):
    date = data['date']
    student_feeding_category = data['student_feeding_category']

    insert_menu_data(ws, data)

    filepath = f"export/exported_files/menu/Меню {student_feeding_category} {date}.xlsx"
    print(f"create_menu_file:{filepath}")
    return filepath


def insert_menu_data(ws, data):
    ws["F1"] = data['date'].strftime('%d.%m.%Y')
    date_cell = ws["F1"]
    ws.column_dimensions[date_cell.column_letter].width = 15

    ws['A2'] = f"Меню {data['student_feeding_category']}"
    menu_cell = ws['A2']

    date_cell.font = bold_font()
    menu_cell.font = bold_font()

    ws.merge_cells("A2:F2")
    menu_cell.alignment = center_aligment()

    insert_row(ws=ws, row_index=3,
               data=("Выход, г",
                     "Наименование блюда",
                     "Калорийность, ккал",
                     "Белки, г", "Жиры, г",
                     "Углеводы, г"),
               alignment=center_aligment())

    for cell in (ws['A3'], ws['B3'], ws['C3'], ws['D3'], ws['E3'], ws['F3']):
        cell.alignment = center_aligment()

    ws.column_dimensions[ws['B3'].column_letter].width = 40

    ws.column_dimensions[ws['C3'].column_letter].width = 20

    i = 4
    for menu_el in data["menu"]:
        ws[f"A{i}"] = menu_el["meal_type"]
        ws.merge_cells(f"A{i}:F{i}")
        ws[f"A{i}"].font = bold_font
        ws[f"A{i}"].alignment = center_aligment()
        i += 1

        for dishes_el in menu_el["dishes"]:
            insert_row(ws=ws,
                       row_index=i,
                       data=(dishes_el["volume_per_student"],
                             dishes_el["dish"],
                             dishes_el["calories"],
                             dishes_el["proteins"],
                             dishes_el["fats"],
                             dishes_el["carbohydrates"]))
            i += 1

        insert_row(ws=ws,
                   row_index=i,
                   data=(f"Итого за {menu_el['meal_type'].lower()}:",
                         "",
                         menu_el['calories'],
                         menu_el['proteins'],
                         menu_el['fats'],
                         menu_el['carbohydrates']))

        ws.merge_cells(f"A{i}:B{i}")
        i += 1

    return i
