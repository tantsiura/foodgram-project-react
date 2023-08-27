from rest_framework.permissions import SAFE_METHODS, BasePermission


class AdminOrReadOnly(BasePermission):
    '''Access rights for the administrator.'''

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user
            and request.user.is_superuser
        )


class AuthorOrReadOnly(BasePermission):
    '''Access rights only for the author or administrator.'''

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class AdminOrAuthor(BasePermission):
    '''Access rights for the author and administrator.'''

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user == obj.author
            or request.user.is_superuser
        )
