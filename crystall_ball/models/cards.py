from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.db import models
from log import log


class Cards(models.Model):
    name = models.CharField(
        'Карта таро',
        max_length=65
    )
    image = models.ImageField(
        'Изображение',
        upload_to='cards/',
        null=True,
        blank=True
    )
    position = models.BooleanField(
        'Прямое положение',
        null=True,
        blank=True,
    )
    number_of_card = models.SmallIntegerField(
        'Number of card'
    )

    class Meta:
        verbose_name = 'Карта Таро'
        verbose_name_plural = 'Карты Таро'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.image:
            path_image = f'cards/{settings.CARD_IMAGES}({self.number_of_card}).jpg'
            card_image = Path(settings.MEDIA_ROOT) / path_image
            log.info(f'CARD IMAGE: current card image {card_image}')
            if card_image.exists():
                with open(card_image, 'rb') as ci:
                    self.image.save(card_image.name, File(ci))
            else:
                log.warning('CARD IMAGE: card image not exist.')
        super().save(*args, **kwargs)