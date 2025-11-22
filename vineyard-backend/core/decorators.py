from django.contrib.auth.decorators import user_passes_test


def head_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and u.role == "head", login_url="login"
    )(view_func)
    return decorated_view_func


def staff_required(view_func):
    decorated_view_func = user_passes_test(
        lambda u: u.is_authenticated and u.role == "head" or u.role == "teacher",
        login_url="login",
    )(view_func)
    return decorated_view_func
