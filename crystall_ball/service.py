import os
import logging

from django.conf import settings
from gigachat import GigaChat

from log import log

logger = logging.getLogger('crystall_ball')


def get_tarot_interpretation(card_names: list) -> str:
    """Генерирует трактовку расклада Таро через GigaChat API.

    Args:
        card_names: Список из 3 названий карт на русском.

    Returns:
        Текст трактовки или сообщение об ошибке.
    """
    cards_str = ', '.join(card_names)
    prompt = f"Трактуй расклад Таро 3 карты: {cards_str}"

    logger.info(f"GigaChat prompt: {prompt}")

    try:
        with GigaChat(
            credentials=os.getenv('GIGACHAT_KEY'), # Ключ авторизации из личного кабинета
            scope='GIGACHAT_API_PERS',
            model="GigaChat-2",
            verify_ssl_certs=False#settings.DEBUG,
        ) as gigachat:
            response = gigachat.chat(prompt)
            interpretation = response.choices[0].message.content
            logger.info(f"GigaChat response: {interpretation}")
            return interpretation
    except Exception as e:
        logger.error(f"GigaChat API error: {e}")
        return 'Не удалось получить трактовку. Попробуйте позже.'
