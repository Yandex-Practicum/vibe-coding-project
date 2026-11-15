# Учебный Django JSON API

Небольшой учебный проект для практики Django без Django REST Framework и без отдельного фронтенда. API построен на обычных Django views и `JsonResponse`.

## Требования

- Python 3.10 или новее
- Django 5.2 LTS

## Структура

```text
config/              настройки, корневые URL и health endpoint
users/               регистрация пользователей
orders/              заказы, их выдача и отмена
course_data/         безопасные файлы для учебных упражнений
manage.py            утилита управления Django
requirements.txt     зависимости проекта
```

В проекте используется стандартная модель `django.contrib.auth.models.User`. Модель пользователя не переопределяется.

## Установка на macOS и Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
```

## Установка на Windows

PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
```

Если политика PowerShell запрещает запуск скрипта активации, можно выполнить команды через `.venv\Scripts\python.exe` без активации окружения.

## Запуск и тесты

Запустить тесты:

```bash
python manage.py test
```

Запустить локальный сервер:

```bash
python manage.py runserver
```

По умолчанию сервер будет доступен по адресу `http://127.0.0.1:8000/`.

## Endpoints

- `GET /api/health/` — проверка работоспособности.
- `POST /api/users/register/` — регистрация по полям `email` и `password`.
- `GET /api/orders/` — заказы текущего пользователя; необязательный фильтр `?status=new`, `?status=paid` или `?status=cancelled`.
- `POST /api/orders/<id>/cancel/` — отмена своего заказа в статусе `new` или `paid`.

Пример проверки health:

```bash
curl http://127.0.0.1:8000/api/health/
```

Пример регистрации:

```bash
curl -X POST http://127.0.0.1:8000/api/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"student@example.com","password":"safe-pass-123"}'
```

## Учебные ограничения

Это учебный, а не production-проект. В настройках намеренно включён `DEBUG`, используется локальная SQLite и указан небезопасный ключ разработки.

Только endpoint регистрации помечен `csrf_exempt`, чтобы JSON-запрос можно было отправить из `curl` без получения CSRF-токена. В реальном приложении такое исключение нужно тщательно оценивать и сочетать с подходящей схемой аутентификации и защитой от злоупотреблений.

Endpoints заказов используют стандартный `login_required` и сессионную аутентификацию Django. Неавторизованный JSON-запрос получает обычный redirect на страницу входа, а не JSON-ошибку. Это явно оставлено как учебное ограничение, чтобы не создавать самописную token-auth и не подключать отдельный auth framework. В тестах авторизация выполняется через Django test client.

## Задания курса

### Тема 2. Знакомство с SourceCraft

1. Изучите `users/views.py` и `users/tests/test_registration.py`.
2. Добавьте в `users/tests/test_registration.py` только тест `test_duplicate_email_returns_400`.
3. В тесте дважды отправьте один email и проверьте, что второй ответ имеет статус `400`, тело `{"error": "email_taken"}`, а в базе остался один пользователь.
4. Запустите:

```bash
python manage.py test users.tests.test_registration
```

Дополнительно изучите `orders/services.py` и объясните, почему бизнес-логика отмены вынесена из view.

Файл `course_data/ignored-context.md` не содержит настоящих секретов, но закрыт правилом в `.codeassistantignore`. Он нужен, чтобы безопасно проверить, как Code Assistant сообщает о заблокированном контексте.

### Тема 3. Промпты и контекст

Добавьте в `GET /api/orders/` необязательный query-параметр `min_total`:

- корректное конечное неотрицательное десятичное значение оставляет заказы с `total >= min_total`;
- строка, которую нельзя разобрать как число, `NaN`, `Infinity` или отрицательное значение возвращают `400` и `{"error": "invalid_min_total"}`;
- без параметра текущее поведение не меняется;
- существующий фильтр `status`, формат JSON и сортировка сохраняются;
- модель, миграции и зависимости менять не нужно.

Добавьте три тестовых метода в `orders/tests/test_list.py`: успешную фильтрацию, неверное значение и отрицательное значение. В тесте неверного значения проверьте обычную строку, `NaN` и `Infinity` через `subTest`. После выполнения задания в модуле должно проходить 6 тестов, а во всём проекте — 15.
