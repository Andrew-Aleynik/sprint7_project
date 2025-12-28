from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
User.Meta.verbose_name = "Пользователь"
User.Meta.verbose_name_plural = "Пользователи"


class Floor(models.Model):
    number = models.PositiveSmallIntegerField(
        unique=True, choices=[(1, "1"), (2, "2"), (3, "3")], verbose_name="Номер"
    )
    name = models.CharField(max_length=50, blank=True, verbose_name="Название")

    class Meta:
        verbose_name = "Этаж"
        verbose_name_plural = "Этажи"

    def __str__(self):
        return f"Этаж {self.number}" + (f" - {self.name}" if self.name else "")


class Hall(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название")
    floor = models.ForeignKey(
        Floor, on_delete=models.CASCADE, related_name="halls", verbose_name="Этаж"
    )

    class Meta:
        verbose_name = "Зал"
        verbose_name_plural = "Залы"

    def __str__(self):
        return f"{self.name}"


class Exhibit(models.Model):
    STATUS_CHOICES = [
        ("undefined", "Неизвестно"),
        ("on_display", "На экспозиции"),
        ("in_storage", "На складе"),
        ("on_restoration", "На реставрации"),
        ("on_loan", "В аренде"),
        ("removed", "Списан"),
    ]

    name = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="undefined",
        verbose_name="Текущий статус",
    )
    hall = models.ForeignKey(
        Hall,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Зал",
        help_text="Только если статус — 'На экспозиции'",
    )
    last_movement_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Экспонат"
        verbose_name_plural = "Экспонаты"

    def __str__(self):
        return f"{self.name}"


class ExhibitImage(models.Model):
    exhibit = models.ForeignKey(
        Exhibit,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Экспонат",
    )
    image = models.ImageField(upload_to="exhibits/", verbose_name="Фото")

    class Meta:
        verbose_name = "Фото экспоната"
        verbose_name_plural = "Фото экспонатов"

    def __str__(self):
        return f"Фото для {self.exhibit.name}"


class Movement(models.Model):
    ACTION_CHOICES = [
        ("added", "Добавлен в фонд"),
        ("moved_to_hall", "Перемещён в зал"),
        ("sent_to_restoration", "Отправлен на реставрацию"),
        ("returned_from_restoration", "Возвращён из реставрации"),
        ("sent_to_storage", "Отправлен на склад"),
        ("sent_on_loan", "Отдан в аренду"),
        ("returned_from_loan", "Возвращён из аренды"),
        ("removed", "Списан"),
    ]

    exhibit = models.ForeignKey(
        Exhibit,
        on_delete=models.CASCADE,
        related_name="movements",
        verbose_name="Экспонат",
    )
    action = models.CharField(
        max_length=50, choices=ACTION_CHOICES, verbose_name="Действие"
    )
    from_location = models.CharField(
        max_length=100, blank=True, verbose_name="Перемещено из"
    )
    to_location = models.CharField(
        max_length=100, blank=True, verbose_name="Перемещено куда"
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Когда перемещено")
    comment = models.TextField(blank=True, verbose_name="Комментарий")

    class Meta:
        verbose_name = "Перемещение экспоната"
        verbose_name_plural = "Перемещения экспонатов"

    def __str__(self):
        return f"{self.exhibit.name} {self.action} {self.timestamp}"
