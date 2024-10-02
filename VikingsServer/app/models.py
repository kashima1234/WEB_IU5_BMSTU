from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User


class Place(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(default="default.png")
    description = models.TextField(verbose_name="Описание", blank=True)

    square = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Место"
        verbose_name_plural = "Места"
        db_table = "places"


class Expedition(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now(), verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='moderator')

    viking = models.CharField(blank=True, null=True)

    def __str__(self):
        return "Поход №" + str(self.pk)

    def get_places(self):
        return [
            setattr(item.place, "value", item.value) or item.place
            for item in PlaceExpedition.objects.filter(expedition=self)
        ]

    class Meta:
        verbose_name = "Поход"
        verbose_name_plural = "Походы"
        ordering = ('-date_formation', )
        db_table = "expeditions"


class PlaceExpedition(models.Model):
    place = models.ForeignKey(Place, models.DO_NOTHING, blank=True, null=True)
    expedition = models.ForeignKey(Expedition, models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(verbose_name="Поле м-м", blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "place_expedition"
