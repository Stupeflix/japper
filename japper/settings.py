"""
Django settings for japper project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import datetime

import os
import environ

from japper.monitoring.plugins import get_installed_apps


# Load environment
env = environ.Env(
    DEBUG=(bool, False),
    STATIC_ROOT=(str, None),
    ALLOWED_HOSTS=(list, []),
    BROKER_URL=(str, 'amqp://guest:guest@localhost:5672//'),
    RAVEN_DSN=(str, None),
    SITE_URL=(str, 'http://127.0.0.1:8000/'),
    REDIS_LOCATION=(str, '127.0.0.1:6379'),
    REDIS_DB=(int, 7),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'rk)5ko4=78lci42-c1$-*#tgdph!5qzq^qqrfn-gpjvtcs&vd_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = env('ALLOWED_HOSTS')

SITE_URL = env('SITE_URL')

# Application definition
INSTALLED_APPS = get_installed_apps((
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'crispy_forms',
    'menu',
    'raven.contrib.django.raven_compat',

    'japper',
    'japper.monitoring',
    'japper.users',
))

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'japper.urls'

WSGI_APPLICATION = 'japper.wsgi.application'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',

    'japper.monitoring.context_processors.search',
)

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

default_db_env = os.environ.get('DEFAULT_DB', 'postgres')
if default_db_env == 'postgres':
    default_db = 'postgres:///japper'
elif default_db_env == 'mysql':
    default_db = 'mysql://localhost/japper'
elif default_db_env == 'sqlite':
    default_db = 'sqlite://:memory:'
else:
    raise ValueError('invald DEFAULT_DB environment variable: %s'
            % default_db_env)

DATABASES = {
    'default': env.db(default=default_db),
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT')

# Crispy forms settings

CRISPY_TEMPLATE_PACK = 'bootstrap3'

# Celery settings

CELERYBEAT_SCHEDULE = {
    'monitoring:fetch_check_results': {
        'task': 'japper.monitoring.tasks.fetch_check_results',
        'schedule': datetime.timedelta(minutes=1),
    },
    'monitoring:cleanup': {
        'task': 'japper.monitoring.tasks.cleanup',
        'schedule': datetime.timedelta(minutes=5),
    },
}

# Email settings

globals().update(env.email_url(default='smtp://localhost'))

# Auth settings

LOGIN_REDIRECT_URL = 'monitoring_problems'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

# Proxy settings

SECURE_PROXY_SSL_HEADER = ('X-Forwarded-Proto', 'https')

# Celery settings

BROKER_URL = env('BROKER_URL')

RAVEN_CONFIG = {
    'dsn': env('RAVEN_DSN'),
}

# Cache settings

CACHES = {
    'default': {
        'BACKEND': 'redis_lock.django_cache.RedisCache',
        'LOCATION': env('REDIS_LOCATION'),
        'OPTIONS': {
            'DB': env('REDIS_DB')
        }
    }
}
