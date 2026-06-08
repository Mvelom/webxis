from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse_lazy


def _is_employee(user):
    return user.is_active and (user.is_staff or user.is_superuser)


def employee_required(view_func):
    """Staff/admin dashboard access — uses site login, not Django admin login."""
    return user_passes_test(_is_employee, login_url=reverse_lazy("login"))(view_func)
