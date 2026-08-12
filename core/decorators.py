from functools import wraps

from django.contrib.auth.decorators import user_passes_test


def admin_required(view_func):
    """Allow access only to Admin users. Staff cannot use admin-only actions."""
    return user_passes_test(lambda u: u.is_authenticated and u.is_admin(), login_url='login')(view_func)
