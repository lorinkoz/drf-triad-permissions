from functools import reduce

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .matching import match_any
from .settings import TRIAD_PLACEHOLDERS, TRIAD_USER_PERMISSIONS_FUNCTION


def Triads(
    default=[],
    *,
    read=None,
    write=None,
    list=None,
    retrieve=None,
    create=None,
    update=None,
    partial_update=None,
    destroy=None,
    custom_placeholders={},
):
    class TriadPermission(BasePermission):
        def get_parameters(self, request, view, obj):
            actions = {
                "list": list,
                "retrieve": retrieve,
                "create": create,
                "update": update,
                "partial_update": partial_update,
                "destroy": destroy,
            }
            # User permissions
            user_permissions = getattr(request.user, TRIAD_USER_PERMISSIONS_FUNCTION, lambda: [])()
            # Placeholders
            all_placeholders = {**TRIAD_PLACEHOLDERS, **custom_placeholders}
            eval_placeholders = {key: function(request, view, None) for key, function in all_placeholders.items()}
            # Queries
            queries = default or []
            if view.action in actions and actions[view.action] is not None:
                queries = actions[view.action]
            elif write is not None and request.method not in SAFE_METHODS:
                queries = write
            elif read is not None and request.method in SAFE_METHODS:
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
            return reduce(lambda t, p: t or match_any(p, user_permissions, True), queries, False)

    return [TriadPermission]
