from functools import wraps
from django.shortcuts import redirect
from django.utils.http import urlencode

def session_access_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("access_token"):
            # Capture current full path
            next_url = request.get_full_path()
            # Build redirect with ?next=<original_path>
            login_url = f"{redirect('auth_app:login').url}?{urlencode({'next': next_url})}"
            return redirect(login_url)
        return view_func(request, *args, **kwargs)
    return wrapper


def redirect_if_authenticated(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get("access_token"):
            return redirect("store:home")
        return view_func(request, *args, **kwargs)
    return wrapper