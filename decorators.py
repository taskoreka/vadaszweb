from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from functools import wraps


def admin_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='rendszergazda').exists():
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return wrapper

def group_required(group_names):
    if not isinstance(group_names, (list, tuple)):
        group_names = [group_names]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.groups.filter(name__in=group_names).exists():
                return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("Nincs jogosultságod a hozzáféréshez.")
        return _wrapped_view
    return decorator
