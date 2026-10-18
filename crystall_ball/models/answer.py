from django.db import models
from .question import Question


class Answer(models.Model):
    """Ответ на гадание. Хранит интерпретацию, сгенерированную GigaChat."""
    question = models.ForeignKey(
        Question,
        verbose_name='Вопрос',
        on_delete=models.CASCADE,
        related_name='answers',
        null=True,
        blank=True,
    )
    text = models.TextField(
        'Ответ',
    )

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
