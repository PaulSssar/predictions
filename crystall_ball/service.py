import os
import logging

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
            username=os.getenv('GIGACHAT_LOGIN'),
            password=os.getenv('GIGACHAT_PASSWORD'),
            scope='GIGACHAT_API_PERS',
        ) as gigachat:
            response = gigachat.chat(prompt)
            interpretation = response.messages[0].content.strip()
            logger.info(f"GigaChat response: {interpretation}")
            return interpretation
    except Exception as e:
        logger.error(f"GigaChat API error: {e}")
        return 'Не удалось получить трактовку. Попробуйте позже.'
