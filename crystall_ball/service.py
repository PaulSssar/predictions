"""Сервис для создания расклада Таро с AI-интерпретацией."""
import os
import logging
import time
from dataclasses import dataclass
from typing import Any

from gigachat import GigaChat
from gigachat.exceptions import GigaChatException

logger = logging.getLogger(__name__)


class GigaChatUnavailable(Exception):
    """Базовое исключение для ошибок GigaChat."""


class GigaChatTimeout(GigaChatUnavailable):
    """Таймаут запроса к GigaChat."""


class GigaChatBadResponse(GigaChatUnavailable):
    """Некорректный ответ от GigaChat."""


@dataclass(frozen=True)
class ReadingResult:
    """Результат расклада."""
    text: str
    card_names: list[str]


def _get_gigachat_client() -> GigaChat:
    """Создаёт клиент GigaChat из переменных окружения."""
    return GigaChat(
        credentials=os.getenv('GIGACHAT_KEY'),
        scope='GIGACHAT_API_PERS',
        model='GigaChat-2',
        verify_ssl_certs=False,
        response_format={"type": "text"},
    )


def _generate_interpretation(
    card_names: list[str], question: str, request_id: str
) -> str:
    """Генерирует трактовку через GigaChat с retry-логикой."""
    cards_str = ', '.join(card_names)
    prompt = (
        f"Ты — опытный таролог. "
        f"Пользователь задал вопрос: \"{question}\". "
        f"Трактуем расклад Таро из 3 карт: {cards_str}. "
        f"Дай подробную интерпретацию расклада в контексте вопроса. "
        f"Не используй markdown-разметку."
    )

    logger.info(
        "gigachat_prompt",
        extra={"request_id": request_id, "cards_count": len(card_names)},
    )

    max_retries = 2
    for attempt in range(max_retries + 1):
        client: GigaChat | None = None
        try:
            client = _get_gigachat_client()
            response = client.chat(prompt)
            logger.info(response, request_id)
            interpretation = response.choices[0].message.content.strip()
            logger.info(interpretation, request_id)
            logger.info(
                "gigachat_ok",
                extra={"request_id": request_id, "text_length": len(interpretation)},
            )
            return interpretation
        except GigaChatException as e:
            logger.error(
                "gigachat_error",
                extra={"request_id": request_id, "attempt": attempt + 1},
                exc_info=True,
            )
            if attempt < max_retries:
                time.sleep(2 ** (attempt + 1))
                continue
            raise GigaChatBadResponse(f"GigaChat error after {max_retries + 1} attempts: {e}")
        except Exception as e:
            logger.error(
                "gigachat_error",
                extra={"request_id": request_id},
                exc_info=True,
            )
            raise GigaChatUnavailable(f"GigaChat error: {e}")
        finally:
            if client is not None:
                client.close()

    raise GigaChatUnavailable("Unexpected: exhausted retries without raising")


def create_reading(
    *, card_names: list[str], question: str, request_id: str | None = None
) -> ReadingResult:
    """Создаёт расклад из 3 карт и генерирует AI-интерпретацию.

    Args:
        card_names: Список из 3 названий карт на русском.
        question: Вопрос пользователя.
        request_id: Опциональный ID запроса для логирования.

    Returns:
        ReadingResult с текстом трактовки и названиями карт.

    Raises:
        GigaChatTimeout: При таймауте запроса.
        GigaChatBadResponse: При некорректном ответе.
        GigaChatUnavailable: При сетевой ошибке.
    """
    if request_id is None:
        request_id = os.urandom(16).hex()

    if len(card_names) != 3:
        raise ValueError("Expected exactly 3 card names")

    interpretation = _generate_interpretation(card_names, question, request_id)

    return ReadingResult(
        text=interpretation,
        card_names=card_names,
    )
