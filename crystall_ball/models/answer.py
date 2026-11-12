from django.db import models
from crystall_ball.models.question import Question
from crystall_ball.models.category_deck import CategoryDeck

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
    category_deck = models.ForeignKey(
        CategoryDeck,
        verbose_name='Категория колоды',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.text[:50]

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
