"""Telegram bot для сервиса Таро."""
import asyncio
import logging
import os
from uuid import uuid4

import django
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictions.settings")
django.setup()

from django.db import close_old_connections  # noqa: E402

from crystall_ball.service import (  # noqa: E402
    create_reading_by_telegram,
    GigaChatBadResponse,
    GigaChatTimeout,
    GigaChatUnavailable,
)

logger = logging.getLogger(__name__)
router = Router()

TELEGRAM_SAFE_LIMIT = 3800  # reserve for parse_mode / UTF-16 emoji expansion


def _split(text: str, limit: int = TELEGRAM_SAFE_LIMIT) -> list[str]:
    return [text[i : i + limit] for i in range(0, len(text), limit)]


@router.message(Command("reading"))
async def reading_handler(message: Message, command: CommandObject) -> None:
    if message.from_user is None:
        return
    question = (command.args or "").strip()
    if not question:
        await message.answer(
            "Задайте вопрос после команды, например: /reading Что меня ждёт?"
        )
        return

    request_id = uuid4().hex
    try:
        result = await sync_to_async(create_reading_by_telegram)(
            telegram_id=message.from_user.id,
            question=question,
            request_id=request_id,
        )
    except (GigaChatTimeout, GigaChatUnavailable, GigaChatBadResponse):
        logger.warning("reading_failed", extra={"request_id": request_id})
        await message.answer("Сейчас не получается заглянуть в карты. Попробуйте позже.")
        return
    finally:
        await sync_to_async(close_old_connections)()

    chunks = _split(result.text)
    if not chunks:
        await message.answer("Не удалось получить текст расклада.")
        return
    logger.info("reading_ok", extra={"request_id": request_id})
    for chunk in chunks:
        await message.answer(chunk)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
