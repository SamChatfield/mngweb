from django.http import HttpResponseBadRequest

from functools import wraps

def require_ajax(func):
    """Decorator to make a view only accept ajax requests"""
    @wraps(func)
    def decorator(request, *args, **kwargs):
        if request.is_ajax():
            return func(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest()
    return decorator

