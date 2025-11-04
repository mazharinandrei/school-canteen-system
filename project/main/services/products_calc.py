from datetime import timedelta, datetime

from django.utils.timezone import localdate

from .menu_info import get_cycle_menu_day_composition
from ..models import Holiday
from dishes.services import get_dish_composition

from warehouse.services.warehouse_transactions import get_availability_or_zero


def is_holiday(date):
    holidays = Holiday.objects.all()
    for holiday in holidays:
        if holiday.start_date <= date <= holiday.end_date:
            return True
    return False


def exclude_holidays_from_range(start_date, end_date):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    current_date = start_date

    result = []
    while current_date <= end_date:

        if current_date.weekday() < 5:
            if not is_holiday(current_date):
                result.append(current_date)
        current_date += timedelta(days=1)

    return result


def products_calc_by_date_interval(
    start_date, end_date, student_feeding_category, planned_people_number
):
    days = exclude_holidays_from_range(start_date, end_date)
    products_raw = {}
    for day in days:
        composition_elements = get_cycle_menu_day_composition(
            1, day.weekday() + 1, student_feeding_category
        )
        for element in composition_elements:
            for dish in element["dishes"]:
                dish_compositions = get_dish_composition(dish.dish, 200)
                for dish_composition in dish_compositions:

                    try:
                        volume_for_planned_count = (
                            dish_composition.volume_per_portion
                            * planned_people_number
                            / 1000
                        )
                        availability = get_availability_or_zero(
                            dish_composition.product, 1
                        )
                        if not isinstance(availability, int):

                            availability = availability.volume

                        print(
                            f"{volume_for_planned_count} и {availability}, нужно: {volume_for_planned_count - availability}"
                        )
                        if (volume_for_planned_count - availability) > 0:
                            volume_for_planned_count = (
                                volume_for_planned_count - availability
                            )
                        else:
                            volume_for_planned_count = 0

                    except Exception:
                        continue

                    if dish_composition.product in products_raw:
                        products_raw[
                            dish_composition.product
                        ] += volume_for_planned_count
                    else:
                        products_raw[dish_composition.product] = (
                            volume_for_planned_count
                        )

    products_raw = {
        k: v
        for k, v in sorted(products_raw.items(), key=lambda item: item[1], reverse=True)
    }

    products = []
    for key, value in products_raw.items():
        if value > 0:
            products.append(
                {
                    "product": key,
                    "volume": float(value),
                }
            )

    return products


def get_cycle_menu_by_date(today=localdate()):
    week_day = today.weekday() + 1
    iso_week_number = today.isocalendar().week
    week_number = ((iso_week_number - 1) % 4) + 1

    return week_number, week_day
