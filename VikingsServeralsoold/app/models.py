from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, User
from django.db import models


class Place(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    description = models.TextField(max_length=500, verbose_name="Описание",)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    square = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"
        db_table = "places"
        ordering = ("pk",)


class Expedition(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', blank=True,  null=True)

    viking = models.CharField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)

    def __str__(self):
        return "Поход №" + str(self.pk)

    class Meta:
        verbose_name = "Поход"
        verbose_name_plural = "Походы"
        db_table = "expeditions"
        ordering = ('-date_formation', )


class PlaceExpedition(models.Model):
    place = models.ForeignKey(Place, on_delete=models.DO_NOTHING, blank=True, null=True)
    expedition = models.ForeignKey(Expedition, on_delete=models.DO_NOTHING, blank=True, null=True)
    order = models.IntegerField(verbose_name="Поле м-м", default=1)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "place_expedition"
        ordering = ('pk', )
        constraints = [
            models.UniqueConstraint(fields=['place', 'expedition'], name="place_expedition_constraint")
        ]
