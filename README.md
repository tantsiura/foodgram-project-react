# Foodgram project
![Deploy badge](https://github.com/tantsiura/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg) 
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)

### The project is available at

http://158.160.11.231/

### API request examples

Documentation and query examples are in Redoc format.
After launching the project's debug backend server, the documentation will be available at [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/).

### Project Description

Foodgram is a recipe publishing platform. 
The following functions are implemented in the project:
- subscription by authorized users to favorite authors;
- adding recipes to favorites; 
- adding the ingredients needed for cooking to the shopping list;
- shopping list download.

## How to start a project:
- Clone the repository `git@github.com:tantsiura/foodgram-project-react.git`
- Copy files `docker-compose.yaml` and `nginx.conf` from a project in a folder _**infra**_ to the server in `home/<your_username>/docker-compose.yaml` and `home/<your_username>/nginx.conf`:
  ```bash
    scp docker-compose.yml your_username@your_IP:/home/your_username/
    scp nginx.conf your_username@your_IP:/home/your_username/
- Install docker:
    ```bash
    sudo apt install docker.io
- Install docker-compose [official documentation](https://docs.docker.com/compose/install/):
   ```bash
    sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
- Build docker-compose on the server:
    ```bash
    sudo docker-compose up -d --build

- Populate Secrets Actions following the pattern of filling env variables in GitHub Actions:
    ```
    Name:                Content:
    DB_ENGINE            django.db.backends.postgresql # indicate that we are working with postgresql
    DB_NAME              postgres # database name
    POSTGRES_USER        postgres # login to connect to the database
    POSTGRES_PASSWORD    postgres # password to connect to the database (set your own)
    DB_HOST              db # name of the service (container)
    DB_PORT              5432 # port for connecting to the database
    HOST                 # server ip
    USER                 # UserName to connect to the server
    SSH_KEY              # Private access key to connect to the server `cat ~/.ssh/id_rsa`
    PASSPHRASE           # Secret key\passphrase if your ssh key is protected with a passphrase
    TELEGRAM_TO          # id of the user's chat or the chat where the bot will send the success result
    TELEGRAM_TOKEN       # Bot token TG for sending notification
    DOCKER_USERNAME      # Docker username for publishing images
    DOCKER_PASSWORD      # Docker user password
    ```
- Make a commit to the Master/Main branch and the finished project will be deployed on your server

- Run the migrations on the server after launch:

    ```bash
    sudo docker-compose exec backend python manage.py makemigrations
    sudo docker-compose exec backend python manage.py migrate
    ```

- And create superuser:

    ```bash
    sudo docker-compose exec backend python manage.py createsuperuser
    ```

- Filling the database manually or using ready-made filling:
    ```bash
    sudo docker-compose exec backend python manage.py shell  
    # execute in the opened terminal:
    >>> from django.contrib.contenttypes.models import ContentType
    >>> ContentType.objects.all().delete()
    >>> quit()
    
    sudo docker-compose exec backend python manage.py loadmodels --path 'data/ingredients.json'
    sudo docker-compose exec backend python manage.py loadmodels --path 'data/tags.json'

    ```
# Technologies
```
Python, Django, HTTP, HTTPS, Django Rest Framework, PostgreSQL, GitHub Actions, DockerHub
```

# Authors

Author: [tantsiura](https://github.com/tantsiura)

![изображение](https://github.com/tantsiura/foodgram-project-react/assets/97056496/65bbe147-ed11-4d8f-8d5b-2b0063e2dd43)
