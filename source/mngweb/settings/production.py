from .base import *


DEBUG = False

LIMS_STATS_CACHE_TIMEOUT = 86400  # 24 hours

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

try:
    from .local import *
except ImportError:
    pass
