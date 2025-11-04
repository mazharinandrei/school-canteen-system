from django.contrib.auth.models import User, Permission
from django.test import TestCase, Client
from django.urls import reverse

from main.models import Grade, StudentFeedingCategory, ApplicationForStudentMeals


class TestApplicationsForMealsPages(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="password123"
        )

        self.student_feeding_category = StudentFeedingCategory.objects.create(
            name="feeding_category111"
        )
        self.grade = Grade.objects.create(
            number=1,
            character="A",
            students_number=10,
            student_feeding_category=self.student_feeding_category,
        )

    def test_list_without_permission(self):
        client = Client()
        client.login(username="testuser", password="password123")

        url = reverse("main:applications_for_student_meals")
        response = client.get(url)

        self.assertEqual(
            response.status_code,
            403,
            msg="You can't view applications without permission",
        )

    def test_list(self):
        self.user.user_permissions.add(
            Permission.objects.get(codename="view_applicationforstudentmeals")
        )

        application = ApplicationForStudentMeals.objects.create(
            date="2024-04-06", grade=self.grade, students_number=9
        )

        client = Client()
        client.login(username="testuser", password="password123")

        url = reverse("main:applications_for_student_meals")
        response = client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, text="feeding_category111")
        self.assertContains(response, text="6 апреля 2024")
        self.assertContains(response, text="1A")
        self.assertContains(response, text=application.students_number)
