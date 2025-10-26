import os

import pandas as pd
from main.models import list_actual_menus

from dishes.services import get_dish_composition

from dishes.models import Product


def abc(value):
    """
  Defines ABC category for given value.

  Parameters
  ----------
  value : float
    Value between 0 and 1.

  Returns
  -------
  str
    "A" if value < 0.5, "B" if value < 0.8, "C" otherwise.

  Notes
  -----
  This function is used to determine ABC category for products in ABC analysis
  report.
  """
    if value < 0.5:
        return "A"
    elif value < 0.8:
        return "B"
    else:
        return "C"


def xyz(value):
    """
    Defines XYZ category for given value.

    Parameters
    ----------
    value : float
      Value between 0 and 1.

    Returns
    -------
    str
      "X" if value < 0.1, "Y" if value < 0.25, "Z" otherwise.

    Notes
    -----
    This function is used to determine XYZ category for products in XYZ analysis
    report.
    """
    if value < 0.1:
        return "X"
    elif value < 0.25:
        return "Y"
    else:
        return "Z"


# Сбор и подготовка данных для отчёта
def get_abc_analysis_data():
    actual_menus = list_actual_menus()
    result = {}
    products = Product.objects.all()

    for menu in actual_menus:

        products_volumes = {}
        for product in products:
            products_volumes[product.name] = 0

        for dish in menu.dishes.all():
            composition = get_dish_composition(dish)
            for el in composition:
                products_volumes[el.product.name] += round(float(el.volume_per_portion), 2)

        result[f"Неделя {menu.week_number},\n{menu.get_week_day_display()}"] = products_volumes

    return result


def categorize_data_by_abc_xyz(data):
    df = pd.DataFrame.from_dict(data)
    df.loc[:, 'За цикл'] = df.sum(axis=1)
    total_volume_of_all_products = df['За цикл'].sum(axis=0)
    df.loc[:, 'Удельный вес'] = df['За цикл'] / total_volume_of_all_products
    df = df.sort_values(by='Удельный вес', ascending=False)
    df.loc[:, 'Кумулятивный удельный вес'] = df['Удельный вес'].cumsum()
    df['Категория A/B/C'] = [abc(x) for x in df['Кумулятивный удельный вес']]
    values = df.loc[:, ~df.columns.isin(['За цикл', 'Удельный вес', 'Кумулятивный удельный вес', 'Категория A/B/C'])]
    df['Коэф. вариации'] = values.std(axis=1, ddof=0) / values.mean(axis=1)
    df['Категория X/Y/Z'] = [xyz(x) for x in df['Коэф. вариации']]
    df.sort_values(by='Категория X/Y/Z')
    df = df.round(2)
    return df


def generate_abc_analysis_table():
    data = get_abc_analysis_data()
    full_table = categorize_data_by_abc_xyz(data)
    return full_table.to_html(classes="table table-striped table-bordered table-sm table_wrapper", justify="justify-all")


def get_detailed_table():
    file_path = os.path.join(os.getcwd(), "export\exported_files\\abc\\abc.xlsx")
    if os.path.exists(file_path):
        return file_path
    else:
        data = get_abc_analysis_data()
        categorize_data_by_abc_xyz(data).to_excel(file_path)
        return file_path

def get_products_by_categories(data = False):
    if not data:
        data = categorize_data_by_abc_xyz(get_abc_analysis_data())
    ax = data[(data['Категория A/B/C'] == "A") & (data['Категория X/Y/Z'] == "X")].index
    ay = data[(data['Категория A/B/C'] == "A") & (data['Категория X/Y/Z'] == "Y")].index
    az = data[(data['Категория A/B/C'] == "A") & (data['Категория X/Y/Z'] == "Z")].index
    bx = data[(data['Категория A/B/C'] == "B") & (data['Категория X/Y/Z'] == "X")].index
    by = data[(data['Категория A/B/C'] == "B") & (data['Категория X/Y/Z'] == "Y")].index
    bz = data[(data['Категория A/B/C'] == "B") & (data['Категория X/Y/Z'] == "Z")].index
    cx = data[(data['Категория A/B/C'] == "C") & (data['Категория X/Y/Z'] == "X")].index
    cy = data[(data['Категория A/B/C'] == "C") & (data['Категория X/Y/Z'] == "Y")].index
    cz = data[(data['Категория A/B/C'] == "C") & (data['Категория X/Y/Z'] == "Z")].index

    return {
        "ax": ax,
        "ay": ay,
        "az": az,
        "bx": bx,
        "by": by,
        "bz": bz,
        "cx": cx,
        "cy": cy,
        "cz": cz
    }
