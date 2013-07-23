# Django settings for project project.
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'NAME': 'dnsAdmin',  # Main database for django
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'edns',
        'PASSWORD': 'secret',
        'HOST': '127.0.0.1'
    },
    'bind': {
        'NAME': 'bind9',  # Database to be replicated to all nameservers
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'edns',
        'PASSWORD': 'secret',
        'HOST': '127.0.0.1'
    }
}

ADMINS = ()
#CACHES = {}
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_ROOT = CUR_DIR + '/static'
STATIC_URL = '/'
MEDIA_ROOT = CUR_DIR + '/media'

MANAGERS = ADMINS
TEMPLATE_DIRS = ()

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.YAMLRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

### db routers #######

DATABASE_ROUTERS = ['project.routers.bindRouter', ]

### end db routers ###

# Additional locations of static files
STATICFILES_DIRS = (
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

AUTH_PROFILE_MODULE = "backend.userProfile"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Bucharest'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

# Language selection
ugettext = lambda s: s
LANGUAGES = (
    ('', ugettext('Auto-detect language')),
    ('en', ugettext('English')),
)
DEFAULT_LANGUAGE = 1

SITE_ID = 1

#LOGIN_URL="login"
APPEND_SLASH = True
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'd+d#qzrp%x@aq-!kewgq75*a4kse!gfy4_%4wkhd_ky@ab&o^)'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'project.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',
    'rest_framework',
    'south',
    'project.api',
    'project.backend',
    'project.stats',
)

MAX_FREE = 5

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/api/v1.0.api'
LOGIN_ERROR_URL = '/login/'

try:
    from local_settings import *
except Exception as err:
    pass
