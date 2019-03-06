"""
Django common settings for prologin project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from collections import namedtuple
import datetime
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))))


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    # Django
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Vendor
    'adminsortable',
    'bootstrapform',
    'bootstrap3',
    'captcha',
    'compat',
    'crispy_forms',
    'datatableview',
    'django_bootstrap_breadcrumbs',
    'django_comments',
    'django_prometheus',
    'djmail',
    'hijack',
    'mptt',
    'reversion',
    'rules.apps.AutodiscoverRulesConfig',
    'statictemplate',
    'tagging',

    # GCC apps
    'gccsite',
    'oauth',
    'centers',
    'users',
    'gcc',

    # Django and vendor, at the bottom for template overriding
    'django.contrib.admin',

    # Debug Toolbar (will not load if DEBUG = False)
    'debug_toolbar',
)

MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',
    'oauth.middleware.RefreshTokenMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'zinnia.context_processors.version',
            ],
        },
    },
]

ROOT_URLCONF = 'gccsite.urls'

WSGI_APPLICATION = 'gccsite.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'fr'

LANGUAGES = (
    ('en', _("English")),
    ('fr', _("French")),
)

TIME_ZONE = 'Europe/Paris'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

USE_I18N = True

USE_L10N = True

FORMAT_MODULE_PATH = [
    'formats',
]

USE_TZ = True

MIGRATION_MODULES = {
    'zinnia': 'news.migrations_zinnia',
}

# Celery (task scheduler)

BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True
CELERY_RESULT_BACKEND = BROKER_URL  # also use redis to store the results
CELERY_RESULT_PERSISTENT = True  # keep results on broker restart
CELERY_TASK_RESULT_EXPIRES = 3600 * 12  # 12 hours

# Emails

DJMAIL_BODY_TEMPLATE_PROTOTYPE = "{name}.body.{type}.{ext}"
DJMAIL_SUBJECT_TEMPLATE_PROTOTYPE = "{name}.subject.{ext}"
DJMAIL_REAL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = "djmail.backends.default.EmailBackend"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

PROJECT_ROOT_DIR = os.path.dirname(BASE_DIR)

STATIC_ROOT = os.path.join(PROJECT_ROOT_DIR, 'public', 'static')
STATIC_URL = '/static/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'gcc.staticfinder.ArchivesStaticFinder',
    'npm.finders.NpmFinder',
)


# Media files (uploaded)

MEDIA_ROOT = os.path.join(PROJECT_ROOT_DIR, 'public', 'media')
MEDIA_URL = '/media/'


# Authentication

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
)
AUTH_USER_MODEL = 'users.GCCUser'

LOGIN_URL = reverse_lazy('users:login')
LOGOUT_URL = reverse_lazy('users:logout')
LOGIN_REDIRECT_URL = reverse_lazy('gcc:index')
USER_ACTIVATION_EXPIRATION = datetime.timedelta(days=7)


AuthTokenClient = namedtuple('AuthTokenClient', ['secret', 'redirect_url'])

# TTL of short-lived access codes.
AUTH_TOKEN_ACCESS_EXPIRATION = datetime.timedelta(minutes=30)
# TTL of auth tokens before asking for a new login flow.
AUTH_TOKEN_REFRESH_EXPIRATION = datetime.timedelta(days=14)
# Registered third-party clients.
AUTH_TOKEN_CLIENTS = {
    # 'client_id: AuthTokenClient('client secret', 'https://callback/url'),
}

# Forum

FORUM_THREADS_PER_PAGE = 25
FORUM_POSTS_PER_PAGE = 20
FORUM_MENTIONS_PER_MESSAGE = 3  # @mention limit to prevent database DoS

# Prologin specific
SITE_HOST = 'gcc.prologin.org'
SITE_BASE_URL = 'https://{}'.format(SITE_HOST)
PROLOGIN_CONTACT_MAIL = 'info@prologin.org'
DEFAULT_FROM_EMAIL = 'Prologin <{}>'.format(PROLOGIN_CONTACT_MAIL)
PROLOGIN_EDITION = None
PROLOGIN_MAX_AVATAR_SIZE = 220
PROLOGIN_MAX_AGE = 21
PROLOGIN_MAX_LEVEL_DIFFICULTY = 9
PROLOGIN_SEMIFINAL_MIN_WISH_COUNT = 1
PROLOGIN_SEMIFINAL_MAX_WISH_COUNT = 3
PROLOGIN_VM_VERSION_PATH = 'http://vm.prologin.org/languages'
LATEX_GENERATION_PROC_TIMEOUT = 60  # in seconds
GOOGLE_ANALYTICS_ID = ''
PROLOGIN_WEBHOOK_BASE_URL = 'https://webhook.prologin.org'
PROLOGIN_WEBHOOK_SECRET = 'changeme'
PROBLEMS_DEFAULT_AUTO_UNLOCK_DELAY = 15 * 60  # in seconds; 15 minutes
PROLOGIN_SEMIFINAL_MODE = False

ARCHIVES_REPOSITORY_PATH = os.path.join(PROJECT_ROOT_DIR, '..', 'archives')
ARCHIVES_REPOSITORY_STATIC_PREFIX = 'archives'

OAUTH_ENDPOINT = 'https://prologin.org/user/auth'
OAUTH_CLIENT_ID = 'gcc'

# Cache durations and keys
CacheSetting = namedtuple('CacheSetting', 'key duration')


# Debug toolbar

def show_toolbar_cb(req):
    from debug_toolbar.middleware import show_toolbar
    if not show_toolbar(req):
        return False
    # Disable for statictemplate
    if req.META['SERVER_NAME'] == 'testserver':
        return False
    return True


DEBUG_TOOLBAR_CONFIG = {
    # Already served
    'JQUERY_URL': '',
    'DISABLE_PANELS': {'debug_toolbar.panels.redirects.RedirectsPanel',
                       # StaticFilesPanel takes *way* too much compute power
                       # while being useless
                       'debug_toolbar.panels.staticfiles.StaticFilesPanel'},
    'SHOW_COLLAPSED': True,
    'SHOW_TOOLBAR_CALLBACK': show_toolbar_cb
}

BOOTSTRAP3 = {'success_css_class': ''}
CRISPY_TEMPLATE_PACK = 'bootstrap3'

# NPM (static assets)
NPM_ROOT_PATH = os.path.join(PROJECT_ROOT_DIR, 'assets')
NPM_STATIC_FILES_PREFIX = 'vendor'
NPM_FILE_PATTERNS = {
    'bootstrap': ['dist/css/*.css', 'dist/js/*.js'],
    'font-awesome': ['css/*.css', 'fonts/*'],
    'jquery': ['dist/*.js'],
}
