from django.db import models


class Answer(models.Model):
    """Поле ответов.Используется для хранения вариантов ответа с
    возможностью дальнейшего увеличения количества вариантов
    через админ-панель"""
    text = models.CharField(
        'Ответ',
        max_length=255
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'