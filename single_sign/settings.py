# coding:utf8
from __future__ import absolute_import
"""
Django settings for single_sign project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from datetime import timedelta
from celery.schedules import crontab


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SESSION_EXPIRE_AT_BROWSER_CLOSE = True


EMAIL_HOST = '117.121.48.85'
EMAIL_HOST_USER = 'cas@100credit.com'
EMAIL_HOST_PASSWORD = 'iK4uJ1gsaG'
EMAIL_SUBJECT_PREFIX = 'CAS'
EMAIL_PORT = 25
EMAIL_USE_TLS = True

MAIN_DOMAIN = 'http://127.0.0.1:8001'

# MAIN_DOMAIN = 'http://cas.100credit.cn'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1-78td1pyo@^+$crd0nwas0*6+4%xt*oiy95qb5qg84&8d0&op'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

LOGIN_URL = '/login/'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cas',
    'dinner',
    'leave',
    'bootstrap3',
    'mypan',
    'workflow',
    'cms',
    'msg',
    'checkin',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'single_sign.urls'

WSGI_APPLICATION = 'single_sign.wsgi.application'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_root')

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'cas_23',
         'USER': 'yu.zhang',
         'PASSWORD': '',
         'HOST': '192.168.162.108',
         'PORT': '3306',
    }
}

MEDIA_ROOT = '/opt/django_project/all_file/CAS/media/'
MEDIA_URL = '/media/'

LANGUAGE_CODE = 'zh-hans'

SITE_ID = 1

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = False

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'single_sign.context_processor.msg',
            ],
        },
    },
]

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [CAS%(name)s] [%(threadName)s] %(levelname)s [%(pathname)s--line:%(lineno)d] %(message)s'             
        },
        'simple': {
            'format': '[%(asctime)s] %(levelname)s %(name)s : %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'error': {
            'level': 'ERROR',
            # 'filters': ['require_debug_false'],
            'class': 'logging.FileHandler',
            'filename': '/opt/django_project/all_file/CAS/log/err.log',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'info.log'),
            'maxBytes': 1024*1024*10,
            'backupCount': 8,
            'formatter': 'simple',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
        'daserr': {
            'handlers': ['file'],
            'level': 'INFO',
        }
    }
}


BOOTSTRAP3 = {
    'jquery_url': '//static/js/jquery.min.js',
    'base_url': '//static/bootstrap-3.3.5/',
    'css_url': None,
    'theme_url': None,
    'javascript_url': None,
    'javascript_in_head': False,
    'include_jquery': False,
    'horizontal_label_class': 'col-md-3',
    'horizontal_field_class': 'col-md-9',
    'set_required': True,
    'set_disabled': False,
    'set_placeholder': True,
    'required_css_class': '',
    'error_css_class': 'has-error',
    'success_css_class': 'has-success',
    'formset_renderers':{
        'default': 'bootstrap3.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'bootstrap3.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'bootstrap3.renderers.FieldRenderer',
        'inline': 'bootstrap3.renderers.InlineFieldRenderer',
    },
}

STATIC_URL = '/static/'
