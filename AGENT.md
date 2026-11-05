# AGENTS.md

## Project overview
Сервис таро: Django-сайт + Telegram-бот (aiogram). Пользователь задаёт вопрос, получает расклад из 3 карт и AI-интерпретацию через GigaChat. Общая бизнес-логика — в `crystall_ball/service.py`, её вызывают и сайт, и бот. Стек: Python 3.12, Django 4.2.5, aiogram 3, PostgreSQL, GigaChat API. Сайт — на Django-шаблонах; DRF не используется.

Текущая структура:
```
crystall_ball/          # Django-приложение: models, views, service.py, admin
users/                  # Django-приложение: пользователи/auth/профиль (уже есть)
predictions/            # настройки проекта (Django settings)
templates/              # HTML-шаблоны
static/                 # CSS/JS/шрифты
bot/                    # НЕТ — создать для aiogram (entrypoint bot/main.py)
```
`users/` и `bot/` — разные вещи. `users/` — Django-app. `bot/` — отдельный пакет с aiogram-кодом, его нужно создать.

## Setup & commands
- Install: `pip install -r requirements.txt`
- Env: создать `.env` вручную. Заполнить `GIGACHAT_KEY` (токен из личного кабинета), `DATABASE_URL`.
- Migrations: `python manage.py migrate`. `python manage.py makemigrations` — **только** при изменении моделей. Сгенерированные файлы вручную не редактировать.
- Run site: `python manage.py runserver`
- Run bot: `python -m bot.main`
- Run tests: **`python manage.py test`** (тестов пока нет; 0 тестов — валидный прогон, не ошибка).
- One test (когда появится): `python manage.py test crystall_ball.tests.test_service.ServiceTest.test_create` — пример, подставь актуальный путь.
- Lint/format/typecheck: **`ruff` и `mypy` в проекте пока не настроены**, `pyproject.toml` отсутствует. См. Quality gates.

## Architecture & conventions
- Слои: `crystall_ball/models.py` → `crystall_ball/service.py` → `crystall_ball/views.py` / `bot/`.
- **Вся бизнес-логика — в `crystall_ball/service.py`.** Никакой логики расклада, выбора карт и вызова GigaChat в views или хендлерах бота.
- Если `service.py` вырастет (> ~500 строк) — разбей на пакет `crystall_ball/services/` с сохранением публичных имён. **Не делай этого заранее.**
- Бот (`bot/`) и сайт (`crystall_ball/views.py`) вызывают **одни и те же функции** из `crystall_ball/service.py`. Не дублируй.
- `users/` — Django-приложение для пользователей/auth. Маппинг `telegram_id → User` — здесь (профиль/identity с `telegram_id: int unique`), **не в `auth.User`**.
- `bot/` — создать. Внутри: `bot/main.py` (entrypoint), при необходимости `bot/handlers/`. Не смешивать с `users/`.
- Результат сервиса — dataclass (Pydantic в проекте пока не используется). Не возвращать raw `dict`.
- Вход в сервис — keyword-only аргументы. Отдельные `*Request`-схемы не заводим.
- Публичные функции сервиса типизированы полностью (аргументы и возврат).
- Сайт — plain Django view + `render()`. JSON-эндпоинт (`JsonResponse`) — только если он уже есть в проекте; новые страницы на JSON не переводить.
- При неоднозначности — **спроси**, а не выбирай наугад.
- Не удаляй и не переименовывай существующие файлы без явной просьбы.
- Перед крупным рефакторингом проверь `git status` и не затирай чужие незакоммиченные изменения.

### Контракт «пользователь» для сервисов
Сайт и бот не передают в один и тот же сервис то `User`, то `int`. Есть два входа, оба ведут к одной приватной функции:
```python
# crystall_ball/service.py
from dataclasses import dataclass

from django.contrib.auth.models import User


@dataclass(frozen=True)
class ReadingResult:
    text: str
    # при необходимости добавь поля (cards: list[str], reading_id: int и т.п.)


def create_reading(
    *, user: User, question: str, request_id: str | None = None
) -> ReadingResult: ...


def create_reading_by_telegram(
    *, telegram_id: int, question: str, request_id: str | None = None
) -> ReadingResult: ...
```
`create_reading_by_telegram` внутри находит/создаёт `User` по `telegram_id` (маппинг — через модель в `users/`) и вызывает общую приватную функцию. Не дублируй логику расклада.

`request_id` опционален: если передан — используется в логах и прокидывается в GigaChat-клиент; если нет — сервис генерирует свой.

### Django в боте
- `django.setup()` вызывается **один раз** в entrypoint `bot/main.py`, после `DJANGO_SETTINGS_MODULE`. Не вызывай `django.setup()` в отдельных модулях бота.
- Async-вызовы ORM и сервисов, трогающих ORM, — через `sync_to_async`.
- `close_old_connections` — после операций с ORM; функция безопасна при частом вызове (закрывает только просроченные соединения).
- Никаких синхронных вызовов ORM из async-хендлеров напрямую.
- `Message.from_user` имеет тип `User | None` — всегда проверяй на `None` перед `.id`.
- Лимит текста Telegram — 4096 символов. Длинный `result.text` — разбивай на части. Учти:
  - если используется `parse_mode` (`HTML`/`MarkdownV2`), режь по абзацам/сущностям, чтобы не разорвать тег;
  - Telegram считает длину в UTF-16 code units, Python `len` — code points; для emoji-heavy текста оставляй запас.

### GigaChat
- Клиент — `crystall_ball/service.py` (пока в одном файле; при росте вынести в `crystall_ball/gigachat_client.py`).
- Обязательны: `timeout` (30 с по умолчанию), `retries` (2 для 5xx и сетевых ошибок), экспоненциальная пауза, кэширование access-токена до истечения.
- 429 от GigaChat — **не ретраить** (пробрасывать сразу как `GigaChatBadResponse`), иначе легко получить бан по квоте. Если политика поменяется — обнови этот раздел.
- Доменные исключения — в `crystall_ball/service.py` (или `crystall_ball/errors.py`, если станет много). Иерархия: `GigaChatTimeout(GigaChatUnavailable)` и `GigaChatBadResponse(GigaChatUnavailable)`. Ловить от частного к общему (`Timeout`/`BadResponse` → `Unavailable`).

| Условие | Исключение | HTTP (JSON) |
|---|---|---|
| timeout (после ретраев) | `GigaChatTimeout` | 504 |
| сетевая ошибка / 5xx после ретраев | `GigaChatUnavailable` | 503 |
| 4xx от GigaChat (включая 429 апстрима), невалидный JSON в 200 | `GigaChatBadResponse` | 502 |

- Все три пробрасываются наверх из сервиса; view/хендлер маппит в HTTP-код (JSON) или в текст ошибки (шаблон/бот).
- Тесты **не должны ходить в сеть**: GigaChat мокается через `unittest.mock.patch` в `setUp`/`setUpTestData` или общий хелпер `crystall_ball/tests/utils.py` (создать вместе с первым тестом).

### Приватность и логирование
- Не логируй текст вопроса пользователя и текст ответа модели целиком. Логируй: `request_id`, длительность, статус, модель, длину ответа, `user_id`/`telegram_id` — без текста.
- `request_id` генерируется в начале обработки (`uuid4().hex` в view/хендлере) и передаётся в сервис. В минимальных примерах ниже он опущен для читаемости; в реальном коде — добавляй.
- В view и хендлере бота — хотя бы одна строка лога на запрос (`logger.info("reading", extra={"request_id": ..., "status": ...})`).
- Не передавай в GigaChat персональные данные, которых нет в вопросе. Не сохраняй сырой ответ модели в БД дольше, чем нужно для отображения.
- Секреты — только из env, не в коде, не в логах.

### Ошибки: шаблоны vs JSON
**Template-views** (страницы сайта):
- Ошибки валидации → перерисовать форму с сообщением в контексте, статус `400`.
- Доменные ошибки GigaChat → отрисовать страницу/фрагмент с текстом «попробуйте позже», статус `502/503/504`.
- Необработанные исключения → стандартный 500 Django.
- Формат тела — HTML шаблона; `{"error": ...}` здесь не используется.

**JSON-эндпоинты** (только если уже есть в проекте; plain Django, без DRF):
- Формат: `{"error": {"code": "...", "message": "..."}}`, без внутренних деталей и без текста вопроса.

| Ситуация | HTTP |
|---|---|
| Валидация запроса | 400 |
| Не аутентифицирован (если это API, а не страница) | 401 |
| Метод не разрешён | 405 |
| Неподдерживаемый Content-Type (если эндпоинт принимает JSON) | 415 |
| Наш rate limit | 429 |
| `GigaChatBadResponse` | 502 |
| `GigaChatUnavailable` | 503 |
| `GigaChatTimeout` | 504 |

- Для template-страниц аутентификация — `@login_required` (302 на логин). `401`/`403` — только для JSON-эндпоинтов, если для них выбран такой контракт.
- Ошибки лимитов на стороне GigaChat → `502/503`, не `429` (429 — только наш лимит).
- JSON-контракт гарантирован только для перечисленных доменных ошибок; необработанные исключения → стандартный 500.
- Если понадобится новый JSON-API — сначала уточни, нужен ли DRF, потом пиши. Не тяни DRF в template-страницы.

## Frontend & design (mystic look)
- Шаблоны: `templates/`, статика: `static/`. Стили — только в `static/css/`, без инлайновых `style=` в шаблонах (кроме динамических переменных).
- Базовый шаблон: `templates/base.html`. Новые страницы наследуют его, не дублируют `<head>` и подключение CSS/JS.
- **Настроение: таинственное, тихое, «лунное».** Не кричащее, не кислотное, без ярких кнопок и стоковых улыбок.
- Палитра: тёмный фон (`#0d0f14`–`#151821`), приглушённые акценты (фиолетовый, серебро, пепел), тёплый свет свечи (`#e8c39e`) только как редкий акцент. Без чистого чёрного и чистого белого.
- Типографика: заголовки — serif с характером (Cormorant, Playfair Display), текст — читаемый sans (Inter, Manrope). Межбуквенный интервал у заголовков чуть шире обычного.
- Атмосфера: мягкие тени, лёгкий туман/градиент, звёзды или пыль на фоне (CSS/SVG, не тяжёлые картинки), плавные появления (`fade-in`, 300–600 мс). Без резких анимаций и мигания.
- Доступность: анимации отключаются при `@media (prefers-reduced-motion: reduce)`; у интерактивных элементов — видимый `:focus-visible`; у изображений — `alt`; контраст ≥ 4.5:1; основной текст ≥ 16px.
- Карты таро: показывать как артефакты — рамка, лёгкая тень, лёгкий поворот **только у декоративной рамки/фона**; текст и подписи не наклонять.
- Читаемость важнее атмосферы.
- Не добавлять внешние CDN и трекеры. Шрифты — локально или через `@font-face`.

## Quality gates

> Текущее состояние: `pyproject.toml` нет, `ruff` и `mypy` не настроены, тестов нет.
> Гейт применяется **по мере появления инструментов**. Не добавляй `pyproject.toml`, `ruff`, `mypy` «молча» — сначала спроси.

**Bootstrap (один раз, если решено внедрять):**
```
pip install ruff mypy django-stubs
# создать pyproject.toml с [tool.ruff] и [tool.mypy]
```

**Гейт (что доступно — то и запускай):**
1. `python manage.py test` — доступно всегда (0 тестов — ок).
2. `ruff check .` — если `ruff` установлен.
3. `ruff format --check .` — если `ruff` установлен.
4. `mypy crystall_ball/ users/ bot/` — если `mypy` установлен.

Если что-то упало — чини, не сдавай. `ruff format .` (без `--check`) в гейте не использовать.

- Новая логика в `crystall_ball/service.py` требует теста в `crystall_ball/tests/` (создать каталог вместе с первым тестом).
- Тесты не должны ходить в сеть: GigaChat и Telegram-API мокаются.
- Вызов GigaChat — всегда с таймаутом, retry и обработкой ошибок (см. раздел GigaChat).
- Не менять бизнес-логику ради красоты.
- Не подключать тяжёлые библиотеки (Three.js, анимационные фреймворки) без явной просьбы.

## Definition of Done
Задача считается завершённой, когда:
- доступные пункты Quality gates зелёные (и явно указано, какие инструменты отсутствуют);
- для новой логики в `crystall_ball/service.py` есть тест;
- примеры кода в этом файле не противоречат правилам (битый пример в `AGENTS.md` — тоже баг);
- в ответе перечислены изменённые файлы, прогнанные команды и что осталось за рамками.

## Do not touch
- `crystall_ball/migrations/`, `users/migrations/` — только через `makemigrations`; не редактировать и не удалять вручную.
- `.env`, `*.pem`, `*.log`
- `bot/session/` — когда появится (сессии aiogram)
- `*.sqlite3`, `media/`, `staticfiles/`, `__pycache__/`, `.venv/`, `*.pyc` (если появятся)

## Язык
Код, имена, комментарии и docstrings — по-английски. Пользовательские тексты (шаблоны, ответы бота, сообщения об ошибках) — по-русски. Общение с разработчиком — по-русски.

## Examples

Плохо (логика в view):
```python
def reading_view(request):
    cards = random.sample(CARDS, 3)  # logic — forbidden
    text = gigachat.ask(...)         # logic — forbidden
```

### Хорошо: template-view

```python
# crystall_ball/views.py
import logging
from typing import cast
from uuid import uuid4

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render

from crystall_ball import service
from crystall_ball.service import (
    GigaChatBadResponse,
    GigaChatTimeout,
    GigaChatUnavailable,
)

logger = logging.getLogger(__name__)


@login_required
def reading_view(request):
    if request.method != "POST":
        return render(request, "crystall_ball/reading_form.html")

    request_id = uuid4().hex
    question = (request.POST.get("question") or "").strip()
    if not question:
        return render(
            request,
            "crystall_ball/reading_form.html",
            {"error": "Вопрос обязателен."},
            status=400,
        )

    try:
        result = service.create_reading(
            user=cast(User, request.user),
            question=question,
            request_id=request_id,
        )
    except GigaChatTimeout:
        logger.warning("reading_timeout", extra={"request_id": request_id})
        return render(
            request,
            "crystall_ball/reading_form.html",
            {"error": "Не дождались ответа. Попробуйте позже."},
            status=504,
        )
    except GigaChatUnavailable:
        logger.warning("reading_unavailable", extra={"request_id": request_id})
        return render(
            request,
            "crystall_ball/reading_form.html",
            {"error": "Сейчас не получается заглянуть в карты. Попробуйте позже."},
            status=503,
        )
    except GigaChatBadResponse:
        logger.warning("reading_bad_response", extra={"request_id": request_id})
        return render(
            request,
            "crystall_ball/reading_form.html",
            {"error": "Сейчас не получается заглянуть в карты. Попробуйте позже."},
            status=502,
        )

    logger.info("reading_ok", extra={"request_id": request_id})
    return render(request, "crystall_ball/reading_result.html", {"result": result})
```

Почему так:
- `request.method != "POST"` на template-view — GET отдаёт пустую форму (200), POST обрабатывается.
- `cast(User, request.user)` — `@login_required` не сужает тип статически; без `cast`/`assert` strict-mypy (когда появится) упадёт на `User | AnonymousUser`.
- `render(..., status=...)` — ошибки валидации и GigaChat возвращаются с корректным HTTP-кодом, но рендерятся шаблоном, а не JSON.
- `except` — от частного к общему; все три класса покрыты.
- `logger` — одна строка на запрос, без текста вопроса/ответа.

### Хорошо: JSON-эндпоинт (только если он уже есть в проекте)

```python
# crystall_ball/views.py
from dataclasses import asdict

from django.http import JsonResponse
from django.views.decorators.http import require_POST


@login_required
@require_POST
def reading_api(request):
    if not request.user.is_authenticated:  # for AJAX a 401 is clearer than a 302 redirect
        return JsonResponse(
            {"error": {"code": "auth", "message": "Требуется вход."}},
            status=401,
        )
    question = (request.POST.get("question") or "").strip()
    if not question:
        return JsonResponse(
            {"error": {"code": "validation", "message": "Вопрос обязателен."}},
            status=400,
        )
    try:
        result = service.create_reading(
            user=cast(User, request.user),
            question=question,
        )
    except GigaChatTimeout:
        return JsonResponse(
            {"error": {"code": "ai_timeout", "message": "Попробуйте позже."}},
            status=504,
        )
    except GigaChatUnavailable:
        return JsonResponse(
            {"error": {"code": "ai_unavailable", "message": "Попробуйте позже."}},
            status=503,
        )
    except GigaChatBadResponse:
        return JsonResponse(
            {"error": {"code": "ai_bad_response", "message": "Попробуйте позже."}},
            status=502,
        )
    return JsonResponse(asdict(result))  # dataclass -> dict; для datetime/UUID — форматируй вручную или добавь Pydantic
```

Если в будущем добавите Pydantic — замените `@dataclass`/`asdict` на `BaseModel`/`model_dump(mode="json")` и обновите этот раздел.

### Хорошо: бот (`bot/` нужно создать)

```python
# bot/main.py
import asyncio
import logging
import os
from uuid import uuid4

import django
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")  # verify name in manage.py
django.setup()

from django.db import close_old_connections  # noqa: E402

from crystall_ball import service  # noqa: E402
from crystall_ball.service import (  # noqa: E402
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
        result = await sync_to_async(service.create_reading_by_telegram)(
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
```

Почему так:
- stdlib и aiogram — до `django.setup()`; после setup импортируются только `crystall_ball.*` и Django-модули, трогающие модели (`# noqa: E402` стоит только там).
- `command.args` — команда не попадает в вопрос.
- `message.from_user is None` — mypy не падает на `union-attr`.
- `request_id` генерируется один раз и передаётся в сервис; в логах он есть.
- `_split` использует запас под `parse_mode` и UTF-16 emoji.
- `close_old_connections` — в `finally` после работы с ORM.
- `if __name__ == "__main__":` — импорт модуля не запускает polling.
