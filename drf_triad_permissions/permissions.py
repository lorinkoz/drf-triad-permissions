import re
from functools import reduce

from rest_framework.permissions import BasePermission, SAFE_METHODS

from .matching import match_any
from .settings import NON_STRICT_PLACEHOLDER, TRIAD_USER_PERMISSIONS_FUNCTION


class PlaceholderWrapper:
    def __init__(self, dicto):
        self.dicto = dicto

    def __getattr__(self, attr):
        return self.dicto.get(attr, NON_STRICT_PLACEHOLDER)


def get_triad_permission(default=[], *, read=None, write=None, **actions):
    class TriadPermission(BasePermission):
        def get_parameters(self, request, view, obj=None):
            # User permissions
            user_permissions = getattr(request.user, TRIAD_USER_PERMISSIONS_FUNCTION, lambda: [])()
            # Placeholders
            verb = request.method.lower()
            action = getattr(view, "action", None)
            placeholders = {
                "verb": verb or NON_STRICT_PLACEHOLDER,
                "action": view.action.replace("_", "-") if action else NON_STRICT_PLACEHOLDER,
                "resource": getattr(view, "permissions_resource", getattr(view, "basename", NON_STRICT_PLACEHOLDER)),
                "url": PlaceholderWrapper(view.kwargs),
                "obj": PlaceholderWrapper(obj.__dict__ if obj else {}),
            }
            # Queries
            queries = default or []
            if verb in actions and actions[verb] is not None:
                queries = actions[verb]
            elif action in actions and actions[action] is not None:
                queries = actions[action]
            elif write is not None and request.method not in SAFE_METHODS:
                queries = write
            elif read is not None and request.method in SAFE_METHODS:
                queries = read
            evaluated_queries = map(
                lambda x: re.sub(r"\w+:" + NON_STRICT_PLACEHOLDER, NON_STRICT_PLACEHOLDER, x.format(**placeholders)),
                queries,
            )
            # Response
            return evaluated_queries, user_permissions

        def has_permission(self, request, view):
            queries, user_permissions = self.get_parameters(request, view, None)
            return reduce(
                lambda t, p: t or match_any(p, user_permissions, strict=not getattr(view, "detail", False)),
                queries,
                False,
            )

        def has_object_permission(self, request, view, obj):
            queries, user_permissions = self.get_parameters(request, view, obj)
            return reduce(lambda t, p: t or match_any(p, user_permissions, strict=True), queries, False)

    return TriadPermission
