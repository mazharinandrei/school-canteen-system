from django.contrib.auth.decorators import permission_required
from django.http import FileResponse

from .services.export_acceptance import generate_acceptance_file
from .services.export_availability import generate_availability_file
from .services.export_costs_of_dishes import generate_costs_of_dishes_file
from .services.export_menu import generate_menu_file
from .services.export_dishes import generate_dishes_file

from .services.export_menu_requirement import generate_menu_requirement_file
from .services.export_products_calc import generate_products_calc_file
from .services.export_tm import generate_technological_map_file
from .services.export_write_off import generate_write_off_file


# Create your views here.


@permission_required("dishes.view_dish")
def export_dishes(request):
    result_path = generate_dishes_file()
    return FileResponse(open(result_path, "rb"), as_attachment=True)


@permission_required("main.view_menu")
def export_menu(request):
    result_path = generate_menu_file(
        date=request.GET.get("date"),
        student_feeding_category=request.GET.get("student-feeding-category"),
    )
    return FileResponse(open(result_path, "rb"), as_attachment=True)


@permission_required("main.view_menu")
def export_menu_requirement(request):
    result_path = generate_menu_requirement_file(
        date=request.GET.get("date"),
        student_feeding_category=request.GET.get("student-feeding-category"),
    )
    return FileResponse(open(result_path, "rb"), as_attachment=True)


def export_products_calc(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    student_feeding_category = request.GET.get("student_feeding_category")
    planned_people_number = int(request.GET.get("planned_people_number"))

    result_path = generate_products_calc_file(
        start_date, end_date, student_feeding_category, planned_people_number
    )
    return FileResponse(open(result_path, "rb"), as_attachment=True)


def export_acceptance(request):
    result_path = generate_acceptance_file()
    return FileResponse(open(result_path, "rb"), as_attachment=True)


def export_write_off(request):
    result_path = generate_write_off_file()
    return FileResponse(open(result_path, "rb"), as_attachment=True)


def export_availability(request):
    result_path = generate_availability_file()
    return FileResponse(open(result_path, "rb"), as_attachment=True)


def export_costs_of_dishes(request):
    result_path = generate_costs_of_dishes_file()
    return FileResponse(open(result_path, "rb"), as_attachment=True)


def export_technological_map(request, tm_id):
    result_path = generate_technological_map_file(tm_id)
    return FileResponse(open(result_path, "rb"), as_attachment=True)
