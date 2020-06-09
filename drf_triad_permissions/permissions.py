from functools import reduce

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .settings import TRIAD_PLACEHOLDERS, TRIAD_USER_PERMISSIONS_FUNCTION


def Triads(
    default=[],
    read=[],
    write=[],
    list=[],
    retrieve=[],
    create=[],
    update=[],
    partial_update=[],
    destroy=[],
    custom_placeholders={},
):
    class TriadPermission(BasePermission):
        def get_parameters(self, request, view, obj):
            # User permissions
            user_permissions = getattr(request.user, TRIAD_USER_PERMISSIONS_FUNCTION, lambda: [])()
            # Placeholders
            all_placeholders = {**TRIAD_PLACEHOLDERS, **custom_placeholders}
            eval_placeholders = {key: function(request, view, None) for key, function in all_placeholders.items()}
            # Queries
            queries = default
            if view.action in actions:
                queries = actions[view.action]
            elif write and request.method not in SAFE_METHODS:
                queries = write
            elif read and request.method in SAFE_METHODS:
                queries = read
            eval_queries = map(lambda x: x.format(**eval_placeholders), queries)
            # Parameters
            return eval_queries, user_permissions

        def has_permission(self, request, view):
            queries, user_permissions = self.get_parameters(request, view, None)
            return reduce(
                lambda t, p: t or match_any(p, user_permissions, not getattr(view, "detail", False)), queries, False,
            )

        def has_object_permission(self, request, view, obj):
            queries, user_permissions = self.get_parameters(request, view, obj)
            return reduce(lambda t, p: t or match_any(p, user_perms, True), queries, False)

    return [TriadPermission]
