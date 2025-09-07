from django.db import models
from django.urls import reverse
from dishes.models import Dish
from django.utils.timezone import localdate
from datetime import timedelta
from django.core.validators import MinValueValidator


# Create your models here.

class MealType(models.Model):
    name = models.CharField('Название приёма пищи',
                            max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Приём пищи'
        verbose_name_plural = 'Приёмы пищи'


class StudentFeedingCategory(models.Model):
    name = models.CharField('Название категории питающихся',
                            max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория питающихся'
        verbose_name_plural = 'Категории питающихся'


def list_actual_menus_for_feeding_category(student_feeding_category):
    cyclic_menus = []
    for i in range(4):
        for week_day in CycleMenu.WeekDay.choices:
            for meal_type in MealType.objects.all():
                try:
                    cycle_menu = CycleMenu.objects.filter(week_number=i + 1,
                                                          week_day=week_day[0],
                                                          meal_type=meal_type.id,
                                                          student_feeding_category=student_feeding_category,
                                                          actual_since__lte=localdate()).latest('actual_since')

                    cyclic_menus.append(cycle_menu)
                except CycleMenu.DoesNotExist:
                    pass
    return cyclic_menus

def count_actual_cycle_menu_days(student_feeding_category):
    days_count = 0
    for i in range(4):
        for week_day in CycleMenu.WeekDay.choices:
            if CycleMenu.objects.filter(week_number=i + 1,
                                                          week_day=week_day[0],
                                                          student_feeding_category=student_feeding_category,
                                                          actual_since__lte=localdate()):
                days_count += 1
    return days_count



def list_actual_menus():
    cyclic_menus = []
    for i in range(4):
        for week_day in CycleMenu.WeekDay.choices:
            for meal_type in MealType.objects.all():
                for student_feeding_category in StudentFeedingCategory.objects.all():
                    try:
                        cycle_menu = CycleMenu.objects.filter(week_number=i + 1,
                                                              week_day=week_day[0],
                                                              meal_type=meal_type.id,
                                                              student_feeding_category=student_feeding_category,
                                                              actual_since__lte=localdate()).latest('actual_since')

                        cyclic_menus.append(cycle_menu)
                    except CycleMenu.DoesNotExist:
                        pass
    return cyclic_menus


class CycleMenu(models.Model):
    class WeekDay(models.IntegerChoices):
        MONDAY = 1, ("Понедельник"),
        TUESDAY = 2, ("Вторник"),
        WEDNESDAY = 3, ("Среда"),
        THURSDAY = 4, ("Четверг"),
        FRIDAY = 5, ("Пятница"),
        SATURDAY = 6, ("Суббота"),
        SUNDAY = 7, ("Воскресенье")

    week_number = models.IntegerField('Номер недели')
    week_day = models.IntegerField("День недели", choices=WeekDay)

    meal_type = models.ForeignKey(MealType, on_delete=models.PROTECT, verbose_name="Приём пищи")
    student_feeding_category = models.ForeignKey(StudentFeedingCategory, on_delete=models.PROTECT,
                                                 verbose_name="Категория питающихся")

    dishes = models.ManyToManyField(
        Dish,
        through="CycleMenuComposition",
        through_fields=('cycle_menu_day', 'dish')
    )
    created_at = models.DateField()
    actual_since = models.DateField()

    def get_composition(self):
        return CycleMenuComposition.objects.filter(cycle_menu_day=self)

    def get_nutrients(self):
        menu_calories, menu_proteins, menu_fats, menu_carbohydrates = 0, 0, 0, 0
        dishes = self.get_composition()
        for dish in dishes:
            dish_calories, dish_proteins, dish_fats, dish_carbohydrates = dish.dish.get_nutrients(volume=dish.volume_per_student)
            menu_calories += dish_calories
            menu_proteins += dish_proteins
            menu_fats += dish_fats
            menu_carbohydrates += dish_carbohydrates
        return menu_calories, menu_proteins, menu_fats, menu_carbohydrates

    def __str__(self):
        return f"Неделя {self.week_number}, {self.get_week_day_display()}, {self.meal_type} для категории {self.student_feeding_category}"

    class Meta:
        verbose_name = 'Цикличное меню'
        verbose_name_plural = 'Цикличное меню'


# Связь блюда и дня цикличного меню
class CycleMenuComposition(models.Model):
    cycle_menu_day = models.ForeignKey(
        CycleMenu,
        on_delete=models.PROTECT)

    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT)

    volume_per_student = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def get_nutrients(self):
        dish_calories, dish_proteins, dish_fats, dish_carbohydrates = self.dish.get_nutrients(volume=self.volume_per_student)
        return dish_calories, dish_proteins, dish_fats, dish_carbohydrates

    def __str__(self):
        return f"{self.cycle_menu_day}: {self.dish}"

    class Meta:
        verbose_name = 'Состав цикличного меню'
        verbose_name_plural = 'Составы цикличного меню'


class MenuRequirement(models.Model):
    date = models.DateField(validators=[MinValueValidator(localdate())], verbose_name="Дата требования")
    
    is_issued = models.BooleanField(default=False)
    is_cooked = models.BooleanField(default=False)
    
    student_feeding_category = models.ForeignKey(
        StudentFeedingCategory,
        on_delete=models.PROTECT,
        verbose_name="Категория питающихся")
    
    students_number = models.IntegerField(validators=[MinValueValidator(1)], verbose_name="Количество учеников")

    dishes = models.ManyToManyField(
        Dish,
        through="MenuRequirementComposition",
        through_fields=('menu_requirement', 'dish'))

    def __str__(self):
        return f"Меню на {self.date} для категории {self.student_feeding_category}"
    
    def get_absolute_url(self):
        return reverse("main:menu", args=[self.date])

    class Meta:
        verbose_name = 'Меню-требование'
        verbose_name_plural = 'Меню-требования'
        unique_together = ('date', 'student_feeding_category')


class MenuRequirementComposition(models.Model):
    menu_requirement = models.ForeignKey(
        MenuRequirement,
        on_delete=models.PROTECT)

    meal_type = models.ForeignKey(MealType,
                                  on_delete=models.PROTECT)  # blank=True, null=True

    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT)

    volume_per_student = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0.1)])

    def __str__(self):
        return f"{self.menu_requirement}: {self.dish}"

    class Meta:
        verbose_name = 'Состав меню'
        verbose_name_plural = 'Составы меню'


class NutrientNormative(models.Model):
    # TODO: норматив устанавливается на день
    created_at = models.DateField(auto_now_add=True)
    actual_since = models.DateField()
    student_feeding_category = models.ForeignKey(StudentFeedingCategory, on_delete=models.PROTECT)
    calories = models.DecimalField(max_digits=8, decimal_places=2)  # TODO: validators = []
    proteins = models.DecimalField(max_digits=8, decimal_places=2)  # TODO: validators = []
    fats = models.DecimalField(max_digits=8, decimal_places=2)  # TODO: validators = []
    carbohydrates = models.DecimalField(max_digits=8, decimal_places=2)  # TODO: validators = []

    def __str__(self):
        return f"Норматив питания для категории {self.student_feeding_category}"

    class Meta:
        verbose_name = 'Норматив нутриентов'
        verbose_name_plural = 'Нормативы нутриентов'


class Holiday(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = 'Праздник'
        verbose_name_plural = 'Праздники'


class Grade(models.Model):
    number = models.IntegerField(verbose_name='Номер класса')
    character = models.CharField(verbose_name='Буква класса', max_length=1)
    students_number = models.IntegerField(verbose_name='Количество учеников')
    student_feeding_category = models.ForeignKey(StudentFeedingCategory,
                                                 on_delete=models.PROTECT,
                                                 verbose_name='Категория питания')

    def __str__(self):
        return f"{self.number}{self.character}"

    class Meta:
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'


class ApplicationForStudentMeals(models.Model):
    date = models.DateField(verbose_name='Дата заявки')
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, verbose_name='Класс')
    students_number = models.IntegerField(verbose_name='Количество учеников')

    def __str__(self):
        return f"Заявка на питание {self.grade} класса от {self.date}"

    def can_be_updated_or_deleted(self):
        if self.date <= localdate() + timedelta(days=2):
            return False
        else:
            return True

    class Meta:
        verbose_name = 'Заявка на питание'
        verbose_name_plural = 'Заявки на питание'