from django.db import models


# Create your models here.


class Positions(models.Model):
    name = models.CharField('Должность',
                            max_length=100)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'


class Staff(models.Model):
    surname = models.CharField('Фамилия',
                               max_length=100)

    name = models.CharField('Имя',
                            max_length=100)

    second_name = models.CharField('Отчество',
                                   max_length=100, blank=True, null=True)

    username = models.OneToOneField('auth.User', on_delete=models.PROTECT, blank=True, null=True)

    position = models.ForeignKey(Positions, on_delete=models.PROTECT, verbose_name='Должность')

    note = models.TextField(blank=True, null=True)  # Поле для примечаний

    def __str__(self):
        return str(self.position) + " " + self.surname_and_initials()

    def full_name(self):
        return self.surname + " " + self.name + " " + self.second_name

    def surname_and_initials(self):
        if self.second_name:
            return self.surname + " " + self.name[0] + "." + self.second_name[0] + "."
        else:
            return self.surname + " " + self.name[0] + "."

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'


def get_staff_by_user(user):
    return Staff.objects.get(username=user.id)