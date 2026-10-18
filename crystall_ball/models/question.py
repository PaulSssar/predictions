from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Question(models.Model):
    """Модель вопроса. Имеет текстовое поле вопроса
    и поле связи с моделью пользователя"""
    text = models.CharField(
        'Вопрос',
        max_length=255
    )
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Вопрос: {self.text} от пользователя: {self.user}'

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'