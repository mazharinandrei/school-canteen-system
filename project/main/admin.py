from django.contrib import admin
from .models import CycleMenu, CycleMenuComposition, MenuRequirement, MenuRequirementComposition, MealType, \
    StudentFeedingCategory, NutrientNormative, Holiday, Grade, ApplicationForStudentMeals

# Register your models here.

admin.site.register(MealType)

admin.site.register(StudentFeedingCategory)

admin.site.register(CycleMenu)
admin.site.register(CycleMenuComposition)

admin.site.register(MenuRequirement)
admin.site.register(MenuRequirementComposition)

admin.site.register(NutrientNormative)

admin.site.register(Holiday)


admin.site.register(Grade)

admin.site.register(ApplicationForStudentMeals)