from django.db import models


class CategoryDeck(models.Model):
    name = models.CharField('Колода', max_length=255)
    slug = models.SlugField('URL', unique=True, help_text='URL-адрес колоды')
    image = models.ImageField(
        'Изображение колоды',
        upload_to='decks/',
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Колода карт'
        verbose_name_plural = 'Колоды карт'
        ordering = ['name']