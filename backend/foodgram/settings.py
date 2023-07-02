import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv("infra/.env")

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJ_SECRET_KEY', default='123')

DEBUG = True

ALLOWED_HOSTS = ["*"]
AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "recipe.apps.RecipeConfig",
    "api.apps.ApiConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "users.apps.UsersConfig",
    "rest_framework",
    'corsheaders',
    "rest_framework.authtoken",
    "djoser",
    "django_filters",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "foodgram.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = 'foodgram.wsgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'ATOMIC_REQUESTS': 'TRUE',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': os.getenv(
                'DB_ENGINE',
                default='django.db.backends.postgresql'),
            'NAME': os.getenv(
                'DB_NAME',
                default='postgres'),
            'ATOMIC_REQUESTS': 'TRUE',
            'USER': os.getenv(
                'POSTGRES_USER',
                default='postgres'),
            'PASSWORD': os.getenv(
                'POSTGRES_PASSWORD',
                default='postgres'),
            'HOST': os.getenv(
                'DB_HOST',
                default='db'),
            'PORT': os.getenv(
                'DB_PORT',
                default='5432')
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        '''
        django.contrib.auth.password_validation
        .''',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_PAGINATION_CLASS":
    "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 6,
}

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SERIALIZERS': {
        'user': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CustomUserSerializer',
        'user_create': 'api.serializers.CustomUserCreateSerializer',
    },
    'PERMISSIONS': {
        'user': ('rest_framework.permissions.IsAuthenticated',),
        'user_list': ('rest_framework.permissions.AllowAny',),
    },
    'HIDE_USERS': False,
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_URLS_REGEX = r"^/api/.*$"

CORS_ALLOWED_ORIGINS = [
    "http://*",
]
CSRF_TRUSTED_ORIGINS = [
    ("http://*localhost"),
    ("https://*localhost"),
    ("http://127.0.0.1:8000/"),
]
