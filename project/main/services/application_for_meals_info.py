from datetime import timedelta

from django.db.models import Sum, F, Q, Value
from django.db.models.functions import Coalesce
from django.utils.timezone import localdate

from main.models import ApplicationForStudentMeals, Grade, StudentFeedingCategory


def get_grades_without_applications():
    tomorrow_applications = ApplicationForStudentMeals.objects.filter(
        date=localdate() + timedelta(days=1),
    )

    grades_not_in_tomorrow_applications = Grade.objects.exclude(
        pk__in=tomorrow_applications.values("grade")
    ).annotate(student_feeding_category_name=F("student_feeding_category__name"))

    return grades_not_in_tomorrow_applications


def get_total_by_student_feeding_category(date=localdate() + timedelta(days=1)):
    grades_without_applications = get_grades_without_applications()
    result = StudentFeedingCategory.objects.annotate(
        total=Coalesce(
            Sum(
                "grade__applicationforstudentmeals__students_number",
                filter=Q(grade__applicationforstudentmeals__date=date),
            ),
            Value(0),
        ),
        student_feeding_category=F("name"),
    ).values("student_feeding_category", "total")
    for row in result:
        row["grades_without_applications"] = grades_without_applications.filter(
            student_feeding_category_name=row["student_feeding_category"]
        )
    return result
