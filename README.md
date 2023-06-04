# Проект Foodgram
![example workflow](https://github.com/tantsiura/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

### Примеры запросов API

Документация и примеры запросов представлены в формате Redoc.
После запуска отладочного web-сервера проекта документация будет доступна по адресу [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/).

### Описание проекта

Foodgram - плтаформа для публикации рецептов. 
В проекте реализованы следующие функции:
- подписка авторизованными пользователями на понравившихся авторов;
- добавление рецептов в избранное; 
- внесение необходимых для приготовления блюд ингредиентов в список покупок;
- скачивание списка покупок.

## Как запустить проект:
- Клонируйте репозиторий `git@github.com:tantsiura/foodgram-project-react.git`
- Скопируйте файлы `docker-compose.yaml` и `nginx/default.conf` из проекта в папке _**infra**_ на сервер в `home/<ваш_username>/docker-compose.yaml` и `home/<ваш_username>/nginx/default.conf` соответственно.
- Установите docker:
    ```bash
    sudo apt install docker.io 
    ```
- Установите docker-compose, с этим вам поможет [официальная документация](https://docs.docker.com/compose/install/).
- Заполните Secrets Actions по шаблону наполнения env переменных в GitHub Actions
    ```
    Наименование:        Содержание:
    DB_ENGINE            django.db.backends.postgresql # указываем, что работаем с postgresql
    DB_NAME              postgres # имя базы данных
    POSTGRES_USER        postgres # логин для подключения к базе данных
    POSTGRES_PASSWORD    postgres # пароль для подключения к БД (установите свой)
    DB_HOST              db # название сервиса (контейнера)
    DB_PORT              5432 # порт для подключения к БД 
    HOST                 194.212.231.123 # ip сервера
    USER                 tantsiura # UserName для подключению к серверу
    SSH_KEY              # Приватный ключ доступа для подключению к серверу `cat ~/.ssh/id_rsa`
    PASSPHRASE           # Серкретный ключ\фраза, если ваш ssh-ключ защищён фразой-паролем
    TELEGRAM_TO          # id чата пользователя или чата куда бот будет отправлять результат успешного выполнения
    TELEGRAM_TOKEN       # Токен бота ТГ для отправки уведомления
    DOCKER_USERNAME      # Имя пользователя Docker для публикации образов
    DOCKER_PASSWORD      # Пароль пользоывателя Docker
    ```
- Сделайте коммит в ветку Master/Main и готовый проект развернется у вас на сервере

- На сервере после запуска выполнить миграции:

    ```bash
    docker-compose exec web python manage.py migrate
    ```

- И создать суперпользователя:

    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```

- Заполнение БД в ручную или используя готовое наполнение
    ```bash
    docker-compose exec web python manage.py shell  
    # выполнить в открывшемся терминале:
    >>> from django.contrib.contenttypes.models import ContentType
    >>> ContentType.objects.all().delete()
    >>> quit()
    
    docker-compose exec web python manage.py loaddata fixtures.json
    ```

# Технологии
```
Python, Django, HTTP, HTTPS, Django Rest Framework, PostgreSQL, GitHub Actions, DockerHub
```

# Авторы

Автор: [tantsiura](https://github.com/tantsiura)
