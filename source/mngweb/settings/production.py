from .base import *


DEBUG = False

ALLOWED_HOSTS = ['.microbesng.uk']
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

LIMS_STATS_CACHE_TIMEOUT = 86400  # 24 hours

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
    from .local import *
except ImportError:
    pass
