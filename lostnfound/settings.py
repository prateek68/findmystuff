import sys
import os
from os.path import abspath, dirname, join, basename

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'findmystuffiiitd@gmail.com'
EMAIL_HOST_PASSWORD = 'fuzzynfringe'
EMAIL_PORT = 587

sys.path.insert(0, '../..')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_PATH = abspath(dirname(__file__))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'FindMyStuff_DB',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    },
    'development': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'lostfound.db'
    }
}
PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
PROJECT_NAME = basename(ROOT_PATH)
TIME_ZONE = 'Asia/Kolkata'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.path.join(PROJECT_ROOT, os.getcwd()+'/media/')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	os.getcwd()+"/static/",
	#os.getcwd()+"/dj/static/",
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = '#$5btppqih8=%ae^#&amp;7en#kyi!vh%he9rg=ed#hm6fnw9^=umc'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lostnfound.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'lostnfound.wsgi.application'

TEMPLATE_DIRS = (
    join(ROOT_PATH, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'suit',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'lostndfound',
    'LnF404',
    # 'social.apps.django_app.default',
    'djrill',
    #'allauth',
    #'allauth.account',
    #'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'bootstrapform',
      )


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
       }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    #'social.apps.django_app.context_processors.backends',
    'allauth.account.context_processors.account',
    'allauth.socialaccount.context_processors.socialaccount',
)

AUTHENTICATION_BACKENDS = (
    # 'social.backends.google.GoogleOpenId',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)
MANDRILL_API_KEY = 'Z_GwF4iDxCx59-24qzr4Nw'
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
EMAIL_HOST_USER='iiitdfindmystuff@gmail.com'
EMAIL_HOST_PASSWORD='kshitij@86'
LOGIN_URL = '/accounts/google/login/'
LOGIN_REDIRECT_URL = '/'
URL_PATH = ''

LnF404_ITEMS_NUMBER = 20

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/google/login'
SOCIALACCOUNT_QUERY_EMAIL = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
    'SCOPE': [
    'https://www.googleapis.com/auth/userinfo.email',
     'https://www.googleapis.com/auth/userinfo.profile',
     'https://www.googleapis.com/auth/plus.login',
     'https://www.googleapis.com/auth/plus.me'
     ],
     'AUTH_PARAMS': {'access_type': 'online'}
    }
}
SOCIALACCOUNT_ADAPTER = 'lostndfound.views.LoginAdapter'

ITEMS_PER_LOCATION = 4

FACEBOOK_PAGE_ID = 0
FACEBOOK_AUTHENTICATION_TOKEN = ""

ALLOWED_LOGIN_HOSTS = ['iiitd.ac.in']

ALLOWED_HOSTS = ['findmystuff.iiitd.edu.in']

try:
    from lostnfound.local_settings import *
except ImportError:
    pass
