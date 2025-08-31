import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = "django-insecure-mktnp&%&_ma&=_&dhlqc%37yp&31n6%mis5vv@-n%loq$8sx5%"

DEBUG = True#False

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "sorl.thumbnail",
    "crystall_ball.apps.CrystallBallConfig",
    "users.apps.UsersConfig",
    #"debug_toolbar",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    #"debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "predictions.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = "predictions.wsgi.application"


DATABASES = {
    'default': {
        'ENGINE': os.getenv('DB_ENGINE', default="django.db.backends.postgresq"),
        'NAME': os.getenv('DB_NAME', default="postgres"),
        'USER': os.getenv('POSTGRES_USER',  default="postgres"),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', default="postgres"),
        'HOST': os.getenv('DB_HOST', default="127.0.0.1"),
        'PORT': os.getenv('DB_PORT', default=5432)
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'srv', 'predictions', 'public',  'static')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LANGUAGE_CODE = "ru"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

INTERNAL_IPS = [
    "127.0.0.1",
]


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
