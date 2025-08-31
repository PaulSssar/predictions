from django.db import models


class Cards(models.Model):
    name = models.CharField(
        'Карта таро',
        max_length=65
    )
    image = models.ImageField(
        'Изображение',
        upload_to='cards/'
    )

    class Meta:
        verbose_name = 'Карта Таро'
        verbose_name_plural = 'Карты Таро'

    def __str__(self):
        return self.name