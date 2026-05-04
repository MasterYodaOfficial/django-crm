# Архитектура CRM

См. также:

- [README](../README.md)
- [Руководство пользователя](user-guide.md)

## Зафиксированные решения

- Язык: `Python 3.13`
- Фреймворк: `Django 5.2.13 LTS`
- Режим приложения: синхронный `WSGI`
- Локальная БД на ранних этапах: `SQLite`
- Целевая БД для Docker и боевого запуска: `PostgreSQL`
- UI: серверные шаблоны Django + `Bootstrap 5.3`
- Модель пользователей: стандартный `django.contrib.auth.models.User`
- Роли: через `Group` и стандартные permissions
- Активный клиент создается только из потенциального клиента
- Связь `Customer -> Contract`: `one-to-many`
- Вне админки реализуем только CRM-функции; управление пользователями и ролями остается в Django admin

## Почему так

- `Django 5.2` это LTS-ветка, для учебно-боевого CRM это рациональнее, чем короткоживущая `6.0`.
- Для текущего ТЗ async не нужен: основная бизнес-операция это атомарная конверсия лида в активного клиента с созданием контракта, а не высокая I/O-нагрузка.
- SQLite удобен для ранней разработки и миграций, но проект сразу проектируем так, чтобы без переделки перейти на PostgreSQL.
- Для UI достаточно server-rendered подхода: формы, списки, карточки и навигацию делаем на Django templates с аккуратной Bootstrap-версткой без SPA-слоя.
- Контроль качества строим вокруг `ruff`, `pylint`, `mypy` и `pytest`, а pull request в `dev` и `master` проверяем через GitHub Actions.

## Целевая структура проекта

```text
django-crm/
├── django_crm/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── common/
│   │   ├── mixins.py
│   │   ├── services.py
│   │   ├── validators.py
│   │   └── tests/
│   ├── products/
│   ├── advertisements/
│   ├── leads/
│   ├── customers/
│   └── contracts/
├── templates/
│   ├── _base.html
│   ├── registration/
│   ├── products/
│   ├── ads/
│   ├── leads/
│   ├── customers/
│   └── contracts/
├── static/
├── media/
├── tests/
├── docs/
├── Dockerfile
├── compose.yml
├── compose.db.yml
├── .env.example
├── pyproject.toml
└── manage.py
```

## Приложения

### `apps.common`

Общее для проекта:

- базовые миксины доступа;
- общие функции и валидаторы;
- общие тестовые фикстуры;
- возможно, базовые abstract models с `created_at` / `updated_at`.

### `apps.products`

Сущность услуги.

Поля:

- `name` - уникальное имя;
- `description`;
- `price`;
- `is_active`;
- `created_at`, `updated_at`.

### `apps.advertisements`

Рекламные кампании.

Поля:

- `name` - уникальное имя;
- `product` -> `Product`;
- `channel` - `TextChoices`;
- `budget`;
- `start_date`;
- `end_date`;
- `is_active`;
- `created_at`, `updated_at`.

### `apps.leads`

Потенциальные клиенты.

Поля:

- `first_name`;
- `last_name`;
- `middle_name` - опционально;
- `phone`;
- `email`;
- `advertisement` -> `Advertisement`;
- `converted_at` - `null=True`, заполняется при конверсии;
- `created_at`, `updated_at`.

Ограничения:

- индекс на `phone`;
- индекс на `email`;
- при необходимости позже можно добавить нормализацию телефона и уникальность на уровне бизнес-правила.

### `apps.customers`

Активные клиенты.

Поля:

- `lead` -> `Lead`, `OneToOneField`;
- `created_at`, `updated_at`.

Смысл:

- один потенциальный клиент может быть переведен только в одного активного клиента;
- вся контактная информация хранится в `Lead`, а `Customer` обозначает факт конверсии.

### `apps.contracts`

Контракты активного клиента.

Поля:

- `name`;
- `customer` -> `Customer`, `ForeignKey`;
- `product` -> `Product`;
- `document` - `FileField`;
- `signed_at`;
- `valid_until`;
- `amount`;
- `created_at`, `updated_at`.

Смысл:

- у одного активного клиента может быть несколько контрактов;
- каждый контракт привязан и к клиенту, и к услуге;
- это упрощает статистику по выручке и оставляет модель ближе к реальным CRM.

## Связи доменной модели

```text
Product 1 ───< Advertisement 1 ───< Lead 1 ─── 1 Customer 1 ───< Contract
                               \_______________________________/
                                   источник клиента для CRM
```

И дополнительная связь:

```text
Contract >─── 1 Product
```

## Роли и права

### Администратор

- управляет пользователями;
- назначает группы;
- назначает permissions;
- работает через Django admin.

Преднастроенные роли создаются и синхронизируются автоматически после миграций,
а также могут быть пересобраны вручную командой `python manage.py sync_roles`.

### Оператор

- `view/add/change` для `Lead`.

### Маркетолог

- `view/add/change` для `Product`;
- `view/add/change` для `Advertisement`.

### Менеджер

- `view` для `Lead`;
- отдельная операция конверсии `Lead -> Customer`;
- `view/add/change` для `Customer`;
- `view/add/change` для `Contract`.

### Общие права

- все роли могут просматривать статистику рекламных кампаний.

## Views и бизнес-слой

Основной стек:

- Django CBV: `ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`;
- отдельные permission mixins;
- отдельный сервисный слой для бизнес-операций.

UI-слой:

- шаблоны Django;
- `Bootstrap 5.3` как основа для layout, форм, таблиц, карточек, навигации и flash messages;
- без отдельного frontend framework.

Ключевой сервис:

- `convert_lead_to_customer(lead_id, contract_data, actor)`:
  - работает внутри `transaction.atomic()`;
  - блокирует повторную конверсию;
  - создает `Customer`;
  - создает первый `Contract`;
  - проставляет `lead.converted_at`.

Это важнее, чем пытаться делать весь проект "асинхронным".

## Статистика рекламных кампаний

Для каждой рекламной кампании считаем:

- количество лидов;
- количество активных клиентов;
- сумму контрактов по сконвертированным клиентам;
- отношение выручки к рекламному бюджету.

Рекомендуемая формула на первом этапе:

```text
efficiency_ratio = total_contract_amount / budget
```

Если `budget = 0`, возвращаем `NULL` или `"-"` в шаблоне.

Позже можно добавить:

- `profit = total_contract_amount - budget`;
- `roi_percent = ((revenue - budget) / budget) * 100`.

## Что делать с удалением

Для MVP:

- разрешаем обычное удаление тем ролям, у которых это явно предусмотрим в UI и permissions;
- не внедряем soft delete на старте.

Если цель сместится ближе к реальному продакшену, soft delete лучше добавить хотя бы для:

- `Lead`;
- `Customer`;
- `Contract`.

Но это уже отдельное усложнение.

## Настройки и окружения

Нужны отдельные settings-модули:

- `base.py` - общая конфигурация;
- `local.py` - локальная разработка;
- `test.py` - тесты.

Принципы:

- без `DATABASE_URL` локальная разработка использует SQLite;
- если `DATABASE_URL` задан, приложение использует его вне зависимости от среды;
- секреты и внешние адреса не храним в коде.

## Стратегия БД и Docker

Я не рекомендую делать логику вида "приложение само решает, поднимать ли контейнер БД" через флаг в `.env`.

Лучше разделить ответственность:

- приложение знает только про строку подключения `DATABASE_URL`;
- `docker compose` решает, есть встроенный контейнер PostgreSQL или нет.

### Рекомендуемый вариант

#### Режим 1. Быстрый локальный старт без Docker

- нет `DATABASE_URL` -> используется SQLite.

#### Режим 2. Docker с собственной PostgreSQL пользователя

- пользователь задает `DATABASE_URL`;
- поднимается только контейнер приложения;
- отдельного `db` сервиса в compose не требуется.

#### Режим 3. Docker со встроенной PostgreSQL

- используется второй compose-файл `compose.db.yml`;
- он добавляет сервис `db`;
- `DATABASE_URL` указывает на `db:5432`.

Это лучше, чем флаг `DB_ENABLED=true/false`, потому что:

- нет лишней условной логики в приложении;
- app-контейнер всегда настраивается одинаково;
- orchestration остается в Docker Compose, где ей и место.

## Переменные окружения

Минимальный набор:

```dotenv
DJANGO_SETTINGS_MODULE=django_crm.settings.local
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=
CSRF_TRUSTED_ORIGINS=
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@example.com
DJANGO_SUPERUSER_PASSWORD=admin
```

Для встроенной PostgreSQL дополнительно:

```dotenv
POSTGRES_DB=crm
POSTGRES_USER=crm
POSTGRES_PASSWORD=crm
POSTGRES_PORT=5432
```

## Контейнеризация

Целевой runtime:

- `Dockerfile` для приложения;
- `gunicorn` как web server;
- `whitenoise` для статики;
- `media` через volume;
- `entrypoint.sh` для `migrate`, `collectstatic` и, при необходимости, bootstrap-операций.

## CI/CD

Целевой pipeline в GitHub Actions:

1. Установка зависимостей.
2. `pylint`.
3. `pytest`.
4. Сборка Docker image.
5. Публикация в Docker Hub.

Рекомендуемая публикация:

- по `main` -> тег `latest`;
- по git tag -> семантический тег версии;
- дополнительно тег по SHA.

## Что не делать на первом этапе

- не внедрять Celery;
- не внедрять async views ради "современности";
- не делать кастомную модель пользователя без необходимости;
- не усложнять проект отдельным API, если весь ТЗ закрывается серверными шаблонами.

## Практические допущения

- шаблоны из `docs_private/templates_only` можно использовать как основу, но привести URL к `reverse()` и named routes;
- страницы по мере реализации приводим к единому аккуратному Bootstrap-стилю; сначала закрываем функциональность этапа, затем сразу доводим экран до внятного рабочего UI;
- сейчас допускаем физическое удаление записей;
- статистику считаем on-demand ORM-запросами, без кэша;
- файл контракта храним локально через `MEDIA_ROOT`, позже при желании можно вынести в S3-совместимое хранилище.
