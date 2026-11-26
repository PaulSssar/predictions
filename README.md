# 🔮 Таро Онлайн — Сервис гаданий с AI

> Задайте вопрос — получите расклад из 3 карт и интерпретацию от GigaChat-2

![Django](https://img.shields.io/badge/Django-4.2.5-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-336791?style=for-the-badge&logo=postgresql)
![GigaChat](https://img.shields.io/badge/GigaChat-2-FF6B6B?style=for-the-badge)

## ✨ Возможности

- 🃏 Выбор из нескольких колод таро
- 🔮 Расклад из 3 карт с AI-интерпретацией
- 🤖 Telegram-бот для гаданий
- 📱 Адаптивный дизайн в мистическом стиле
- 📊 История всех вопросов и ответов

## 🏗 Архитектура

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Gunicorn   │────▶│  Django App │
│   (port 80) │     │   (port 8000)│     │  + GigaChat │
└─────────────┘     └──────────────┘     └─────────────┘
                              │                    │
                              │                    ▼
                        ┌──────────┐       ┌─────────────┐
                        │PostgreSQL│       │  Telegram   │
                        │ (5432)   │       │    Bot      │
                        └──────────┘       └─────────────┘
```

## 📦 Стек технологий

| Компонент       | Технология      |
|-----------------|-----------------|
| Backend         | Django 4.2.5    |
| Язык            | Python 3.12     |
| База данных     | PostgreSQL 17   |
| Веб-сервер      | Gunicorn        |
| Прокси          | Nginx           |
| AI-модель       | GigaChat-2      |
| Telegram-бот    | aiogram 3.x     |
| Контейнеризация | Docker + Compose|

## 🚀 Быстрый старт

### 1. Клонирование

```bash
git clone <repository-url>
cd predictions
```

### 2. Настройка переменных окружения

Создайте файл `.env`:

```env
# GigaChat API
GIGACHAT_KEY=your_gigachat_api_key

# PostgreSQL
DB_NAME=predictions
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Telegram Bot (опционально)
TELEGRAM_BOT_TOKEN=your_bot_token
```

### 3. Запуск через Docker

```bash
# Сборка и запуск
docker compose up -d --build

# Сборка статических файлов
docker compose exec app python manage.py collectstatic --noinput

# Создание суперпользователя
docker compose exec app python manage.py createsuperuser
```

Сервер доступен по адресу: **http://localhost**

### 4. Запуск Telegram-бота

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск бота
TELEGRAM_BOT_TOKEN=your_bot_token python -m bot.main
```

## 📁 Структура проекта

```
predictions/
├── crystall_ball/          # Основное Django-приложение
│   ├── models/             # Модели данных
│   ├── service.py          # Бизнес-логика (GigaChat)
│   ├── views.py            # Представления
│   ├── admin.py            # Админ-панель
│   └── templatetags/       # Кастомные теги шаблонов
├── users/                  # Пользователи и аутентификация
├── predictions/            # Настройки проекта
├── templates/              # HTML-шаблоны
├── static/                 # CSS, JS, изображения
├── bot/                    # Telegram-бот (aiogram)
├── nginx/                  # Конфигурация Nginx
├── docker-compose.yml      # Оркестрация контейнеров
├── Dockerfile              # Образ приложения
└── requirements.txt        # Зависимости Python
```

## 🎨 Дизайн

Проект выполнен в таинственном «лунном» стиле:
- Тёмные тона с фиолетовыми акцентами
- Плавные анимации и тени
- Адаптивная вёрстка для мобильных устройств
- Доступность (WCAG 4.5:1 контраст)

## 🔒 Безопасность

- Секреты только через переменные окружения
- Логирование без персональных данных
- Защита CSRF и XSS
- Rate limiting на уровне GigaChat API

## 🧪 Разработка

```bash
# Локальный запуск (без Docker)
python manage.py runserver

# Миграции
python manage.py makemigrations
python manage.py migrate

# Сборка статики
python manage.py collectstatic --noinput

# Тесты
python manage.py test
```

## 🐳 Production

```bash
# Запуск в production-режиме
docker compose up -d --build

# Проверка статусов
docker compose ps

# Просмотр логов
docker compose logs -f app
docker compose logs -f nginx
```

## 📝 API

### Telegram-бот

| Команда      | Описание                          |
|-------------|-----------------------------------|
| `/reading`  | Получить расклад Таро             |
| `/help`     | Справка по командам               |

### REST (админ-панель)

| Путь          | Описание              |
|--------------|-----------------------|
| `/admin/`    | Админ-панель Django   |
| `/accounts/` | Аутентификация        |

## 🤝 Вклад

1. Форкните репозиторий
2. Создайте ветку `feature/amazing-feature`
3. Закоммитьте изменения `git commit -m 'Add amazing feature'`
4. Отправьте в ветку `git push origin feature/amazing-feature`
5. Откройте Pull Request

## 📄 Лицензия

MIT

## 📞 Контакты

- Проект открыт для предложений и баг-репортов
- Для вопросов создайте Issue в репозитории

---

✨ *Карты знают всё. Осталось только спросить.* ✨
