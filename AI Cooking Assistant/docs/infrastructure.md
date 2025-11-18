# Документация по инфраструктуре AI Cooking Assistant

## Содержание
- [Инструкции запуска dev окружения](#инструкции-запуска-dev-окружения)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Cheat Sheet для команды](#cheat-sheet-для-команды)

## Инструкции запуска dev окружения

### Предварительные требования
- Docker Desktop 4.12+
- Git 2.35+
- 8GB+ свободной памяти
- Windows/MacOS/Linux



# 1. Клонирование репозитория
git clone <repository-url>
cd "AI Cooking Assistant"

# 2. Настройка окружения
Создайте и отредактируйте .env файл при необходимости

# 3. Запуск приложения
docker-compose build
docker-compose up -d

# 4. Проверка статуса
docker-compose ps




### Troubleshooting Guide 

### Общие проблемы
## Контейнеры не запускаются
Симптомы: Контейнеры в статусе Restarting, Waiting или Unhealthy

Решение:
# 1. Проверьте логи
docker-compose logs

# 2. Проверьте доступность портов
netstat -an | grep <port>

# 3. Пересоберите образы
docker-compose down
docker-compose build --no-cache
docker-compose up -d


## Backend не подключается к базе данных
Симптомы: Connection refused, database does not exist

Решение:

# 1. Проверьте переменные окружения
docker-compose exec backend env | grep DATABASE

# 2. Проверьте доступность БД
docker-compose exec postgres pg_isready -U ${POSTGRES_USER}

# 3. Проверьте существование базы
docker-compose exec postgres psql -U ${POSTGRES_USER} -l

# 4. Переинициализируйте БД
docker-compose down -v
docker-compose up postgres -d
sleep 10
docker-compose up backend -d

## Frontend не запускается
Симптомы: npm ERR!, Module not found, бесконечная загрузка

Решение:

# 1. Проверьте зависимости
docker-compose exec frontend npm list

# 2. Переустановите зависимости
docker-compose exec frontend rm -rf node_modules package-lock.json
docker-compose exec frontend npm install

# 3. Проверьте структуру проекта
docker-compose exec frontend ls -la

# 4. Пересоберите образ
docker-compose build frontend --no-cache

## Health check fails
Симптомы: Контейнеры остаются в статусе starting

Решение:

# Временно отключите healthcheck в docker-compose.yml
healthcheck:
  disable: true
Или увеличьте таймауты:
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 30s
  retries: 5
  start_period: 60s
Проблемы с ресурсами

## Нехватка памяти Docker
Симптомы: Контейнеры убиваются, OOM error

Решение:

Увеличьте лимит памяти в Docker Desktop до 6GB+

Остановите неиспользуемые контейнеры: docker system prune


## Конфликт портов
Симптомы: port is already allocated

Решение:

# Найдите процесс использующий порт
lsof -i :3000

# Или измените порты в docker-compose.yml
ports:
  - "3001:3000"  # вместо 3000:3000
Полезные команды для диагностики
bash
# Проверка статуса всех контейнеров
docker-compose ps

# Просмотр логов в реальном времени
docker-compose logs -f <service-name>

# Проверка использования ресурсов
docker stats

# Проверка сети
docker network ls
docker network inspect <network-name>

# Вход в контейнер для отладки
docker-compose exec <service-name> sh




### Cheat Sheet для команды

## Управление контейнерами

# Запуск всех сервисов
docker-compose up -d

# Остановка всех сервисов
docker-compose down

# Перезапуск конкретного сервиса
docker-compose restart backend

# Просмотр логов
docker-compose logs -f backend

# Проверка статуса
docker-compose ps
Разработка
bash
# Запуск в режиме разработки
docker-compose up backend frontend

# Пересборка сервиса
docker-compose build backend --no-cache

# Установка новых зависимостей
docker-compose exec backend pip install <package>
docker-compose exec frontend npm install <package>
База данных
bash
# Подключение к БД
docker-compose exec postgres psql -U ai_cooking_user -d ai_cooking_db

# Резервное копирование
docker-compose exec postgres pg_dump -U ai_cooking_user ai_cooking_db > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U ai_cooking_user -d ai_cooking_db < backup.sql
Отладка
bash
# Вход в контейнер
docker-compose exec backend sh
docker-compose exec frontend sh

# Проверка здоровья
curl http://localhost:8000/health
curl http://localhost:3000

# Проверка сети
docker network inspect aicookingassistant_app-network
📁 Структура проекта
text
AI Cooking Assistant/
├── 📁 backend/           # FastAPI приложение
│   ├── 📁 init/         # SQL скрипты инициализации
│   ├── main.py          # Точка входа
│   ├── requirements.txt # Python зависимости
│   └── Dockerfile.dev   # Docker образ для разработки
├── 📁 frontend/         # Next.js приложение
│   ├── 📁 pages/        # React компоненты
│   ├── package.json     # Node.js зависимости
│   └── Dockerfile.dev   # Docker образ для разработки
├── 📁 llm-service/      # Jupyter сервис
│   ├── requirements.txt
│   └── Dockerfile.dev
├── 📁 docs/            # Документация
├── docker-compose.yml   # Оркестрация контейнеров
├── .env                # Переменные окружения
└── .env.example        # Шаблон переменных окружения

## Полезные скрипты
Очистка системы

# Остановка и удаление всех контейнеров
docker-compose down -v --remove-orphans

# Очистка неиспользуемых образов
docker image prune -f

# Очистка системы Docker
docker system prune -f
Мониторинг
bash
# Просмотр использования ресурсов
docker stats

# Просмотр логов в реальном времени
docker-compose logs -f --tail=100

# Проверка дискового пространства
docker system df

## Экстренные случаи
Сервис не отвечает
bash
# Принудительный перезапуск
docker-compose restart <service-name>

# Если не помогает - полный перезапуск
docker-compose down && docker-compose up -d
Проблемы с базой данных
bash
# Сброс базы данных (ОСТОРОЖНО!)
docker-compose down -v
docker-compose up postgres -d
Проблемы с зависимостями
bash
# Переустановка всех зависимостей
docker-compose build --no-cache
