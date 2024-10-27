# Foodgram: Продуктовый помощник

Foodgram — это веб-сервис для обмена рецептами, где пользователи могут делиться кулинарными находками, сохранять понравившиеся рецепты, подписываться на интересных авторов и скачивать список продуктов для готовки. Приложение удобно структурировано, имеет открытый API для взаимодействия с внешними сервисами и легко разворачивается с помощью Docker.

## Основные возможности:

* Публикация рецептов с указанием ингредиентов, их количества и пошаговым описанием.
* Подписки на авторов и отслеживание обновлений в их рецептах.
* Добавление рецептов в Избранное и генерация списка покупок.

## Как развернуть проект на сервере

### Подготовка окружения: 
Установите Docker и Docker Compose
```
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt install docker-compose-plugin
```
### Клонирование репозитория: 
Склонируйте проект на сервер
```
git clone git@github.com:cubaser/foodgram.git
```
### Подготовка переменных окружения: 
Настройте переменные для контейнеров. В корневой директории переименуйте myenv.env в .env и добавьте свои значения

* POSTGRES_USER=foodgram_user
* POSTGRES_PASSWORD=foodgram_password
* POSTGRES_DB=foodgram
* DB_NAME=foodgram
* DB_HOST=db
* DB_PORT=5432
* SECRET_KEY=secret_key_django_project
* DEBUG=False
* ALLOWED_HOSTS=127.0.0.1,localhost

### Сборка и запуск контейнеров: 
Перейдите в папку infra и выполните
```
docker compose up --build
```
### Подготовка базы данных: 
После запуска выполните миграции, создайте суперпользователя и соберите статику
```
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py collectstatic 
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```
## Локальный запуск проекта

Для локального запуска клонируйте репозиторий и настройте переменные окружения, как описано выше. Запуск осуществляется командой docker compose up из директории /infra.
Для локального запуска клонируйте репозиторий и настройте переменные окружения, как описано выше. Запуск осуществляется командой docker compose up из директории /infra.

После успешного запуска проект будет доступен по адресу http://localhost/.
Используемые технологии

* Backend: Python, Django, Django REST Framework
* Frontend: React (файлы собираются при старте контейнера)
* База данных: PostgreSQL
* Веб-сервер и прокси: NGINX
* Контейнеризация и развёртывание: Docker, Docker Compose
* CI/CD: GitHub Actions для автоматической проверки, сборки и деплоя

Адрес сайта https://foodgram.sytes.net/

Автор

Иванов Виктор

Разработчик Python и Django
