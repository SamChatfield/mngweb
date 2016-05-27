from .base import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

for template_engine in TEMPLATES:
    template_engine['OPTIONS']['debug'] = True


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LIMS_STATS_CACHE_TIMEOUT = 500

try:
    from .local import *
except ImportError:
    pass
