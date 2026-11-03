from rest_framework.permissions import IsAuthenticated as DRFIsAuthenticated

from core.exceptions import NotAuthenticatedError


class IsAuthenticated(DRFIsAuthenticated):
    """
    Allows access only to authenticated users with 401 Error to unauthenticated users.
    """

    def has_permission(self, request, view):
        if super().has_permission(request, view):
            return True
        raise NotAuthenticatedError()
