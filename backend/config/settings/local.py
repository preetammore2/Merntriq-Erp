from .base import *  # noqa: F403,F401

DEBUG = True

if not env.bool("DJANGO_LOCAL_USE_REDIS", default=False):  # noqa: F405
    CACHES = {  # noqa: F405
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "mentriq360-local-dev",
        }
    }
