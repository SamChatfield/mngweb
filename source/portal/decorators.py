import requests

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from allauth.account.decorators import verified_email_required
from .services import limsfm_get_project_permissions
from .utils import (user_is_project_contact, user_is_project_owner,
                    handle_limsfm_http_exception, handle_limsfm_request_exception)


def check_project_permissions(owner=False):
    """Check project permissions"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if user.is_staff:  # allow staff to access all projects
                return func(request, *args, **kwargs)

            permissions = None
            try:
                permissions = limsfm_get_project_permissions(kwargs['project_uuid'])
            except requests.HTTPError as e:
                handle_limsfm_http_exception(request, e)
            except requests.RequestException as e:
                handle_limsfm_request_exception(request, e)
            if not permissions:
                return render(request, 'portal/project.html', {'project': None})

            login_required = permissions['portal_login_required']
            if owner:
                user_allowed = user_is_project_contact(user, permissions)
            else:
                user_allowed = user_is_project_owner(user, permissions)

            if login_required:
                if user.is_authenticated():
                    if not user_allowed:
                        raise PermissionDenied
                else:
                    return verified_email_required(func)(request, *args, **kwargs)

            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_project_contact_permissions(func):
    return check_project_permissions(owner=False)(func)


def check_project_owner_permissions(func):
    return check_project_permissions(owner=True)(func)
