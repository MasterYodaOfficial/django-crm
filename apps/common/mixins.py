"""Mixins shared across CRM views."""

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponseRedirect


class LoginAndPermissionRequiredMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Redirect anonymous users to login and return 403 to logged-in users without access."""

    raise_exception = False
    request: HttpRequest

    def handle_no_permission(self) -> HttpResponseRedirect:
        """Send anonymous users to login, deny authenticated users explicitly."""

        if self.request.user.is_authenticated:
            raise PermissionDenied
        return super().handle_no_permission()
