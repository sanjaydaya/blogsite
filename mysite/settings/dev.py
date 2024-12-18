from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '^k-$-)pl5e%_th&&a^u7tfoz%vtp#w64&ex*-=xhzqv@uuxv1u'

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ['*']

# Email backend for local development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS += [
    # 'debug_toolbar',  # Uncomment this line to enable the Debug Toolbar
    'django_extensions',
    'wagtail.contrib.styleguide',  # Wagtail's Styleguide app for styling components
]

MIDDLEWARE += [
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',  # Uncomment this line to enable Debug Toolbar
]

INTERNAL_IPS = ("127.0.0.1", "172.17.0.1")  # For Debug Toolbar

# Uncomment this line to enable template caching for production
# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
#         "LOCATION": "/path/to/your/site/cache"
#     }
# }

# Attempt to import local settings, if available
try:
    from .local import *
except ImportError:
    pass
