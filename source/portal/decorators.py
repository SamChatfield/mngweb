import requests

from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from allauth.account.decorators import verified_email_required
from .services import limsfm_get_project_permissions
from .utils import (user_is_project_contact, user_is_project_owner,
                    handle_limsfm_http_exception, handle_limsfm_request_exception)


def check_project_permissions(view_func=None, owner=False):
    """
    Decorator for portal views that checks whether the user has permission to
    access a project anonymously, as a project contact (collaborator),
    or as project owner. Second positional argument to view_func must be project_uuid.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, project_uuid, *args, **kwargs):
            user = request.user
            if user.is_staff:  # allow staff to access all projects
                return view_func(request, project_uuid, *args, **kwargs)

            permissions = None
            try:
                permissions = limsfm_get_project_permissions(project_uuid)
            except requests.HTTPError as e:
                handle_limsfm_http_exception(request, e)
            except requests.RequestException as e:
                handle_limsfm_request_exception(request, e)
            if not permissions:
                return render(request, 'portal/project.html', {'project': None})

            # when owner=True, always require a login
            login_required = owner or permissions['portal_login_required']
            if owner:
                user_allowed = user_is_project_owner(user, permissions)
            else:
                user_allowed = user_is_project_contact(user, permissions)

            if login_required:
                if user.is_authenticated():
                    if not user_allowed:
                        raise PermissionDenied
                else:
                    return verified_email_required(view_func)(request, project_uuid, *args, **kwargs)

            return view_func(request, project_uuid, *args, **kwargs)
        return wrapper
    if view_func:
        return decorator(view_func)
    return decorator
