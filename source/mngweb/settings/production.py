from .base import *


DEBUG = False

LIMS_STATS_CACHE_TIMEOUT = 86400  # 24 hours

try:
    from .local import *
except ImportError:
    pass
