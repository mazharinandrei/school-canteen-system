from datetime import timedelta

from django.utils.timezone import localdate

from main.models import ApplicationForStudentMeals, Grade, StudentFeedingCategory


def get_total_by_student_feeding_category():
    total_by_student_feeding_category_raw = {}
    total_by_student_feeding_category = []

    today_applications = ApplicationForStudentMeals.objects.filter(
        date=localdate() + timedelta(days=1)
    )

    for student_feeding_category in StudentFeedingCategory.objects.all():
        total_by_student_feeding_category_raw[student_feeding_category] = 0

    for application in today_applications:
        category = application.grade.student_feeding_category
        if category in total_by_student_feeding_category_raw:
            total_by_student_feeding_category_raw[
                category
            ] += application.students_number
        else:
            total_by_student_feeding_category_raw[category] = (
                application.students_number
            )

    for key, value in total_by_student_feeding_category_raw.items():
        total_by_student_feeding_category.append(
            {
                "student_feeding_category": key,
                "total": value,
                "grades_without_applications": get_grades_without_applications(key),
            }
        )

    return total_by_student_feeding_category


def get_grades_without_applications(student_feeding_category):
    result = []
    today_applications = ApplicationForStudentMeals.objects.filter(
        date=localdate() + timedelta(days=1)
    )

    for grade in Grade.objects.filter(
        student_feeding_category=student_feeding_category
    ):
        print(today_applications.filter(grade=grade))
        if not today_applications.filter(grade=grade.id).exists():
            print(grade.id)
            result.append(grade)

    return result
