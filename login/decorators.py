from functools import wraps

from django.shortcuts import redirect


def expa_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        access_token = request.session.get('expa_access_token')
        if not access_token:
            return redirect('login_start')
        return view_func(request, *args, **kwargs)

    return wrapper
