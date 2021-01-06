from functools import reduce

from rest_framework.permissions import BasePermission

from drf_triad_permissions.matching import match_any
from drf_triad_permissions.settings import NON_STRICT_PLACEHOLDER, TRIAD_DIVIDER, TRIAD_USER_PERMISSIONS_FUNCTION

NO_MATCH = "!NOMATCH!"


def clean_no_match(match):
    chunks = match.split(TRIAD_DIVIDER)
    return TRIAD_DIVIDER.join(NON_STRICT_PLACEHOLDER if NO_MATCH in x else x for x in chunks)


class PlaceholderWrapper:
    def __init__(self, dicto):
        self.dicto = dicto

    def __getattr__(self, attr):
        return self.dicto.get(attr, NO_MATCH)


def get_triad_permission(*, allow=None, deny=None, default_resource=None):
    if allow is None:
        allow = []
    if deny is None:
        deny = []

    class TriadPermission(BasePermission):
        def get_parameters(self, request, view, obj=None):
            # User permissions
            user_permissions = getattr(request.user, TRIAD_USER_PERMISSIONS_FUNCTION, lambda: [])()
            # Placeholders
            verb = request.method.lower()
            action = getattr(view, "action", None)
            placeholders = {
                "verb": verb or NO_MATCH,
                "action": view.action.replace("_", "-") if action else NO_MATCH,
                "resource": getattr(
                    view,
                    "permissions_resource",
                    default_resource or getattr(view, "basename", NO_MATCH),
                ),
                "url": PlaceholderWrapper(view.kwargs),
                "obj": PlaceholderWrapper(obj.__dict__ if obj else {}),
            }
            # Queries
            evaluated_allow = [clean_no_match(x.format(**placeholders)) for x in allow]
            evaluated_deny = [clean_no_match(x.format(**placeholders)) for x in deny]
            # Response
            return evaluated_allow, evaluated_deny, user_permissions

        def has_permission(self, request, view):
            allow_queries, deny_queries, user_permissions = self.get_parameters(request, view, None)

            def test(queries, reference, strict=True):
                return reduce(lambda t, p: t or match_any(p, reference, strict=strict), queries, False)

            strict_for_allow = not getattr(view, "detail", False)
            return test(allow_queries, user_permissions, strict_for_allow) and not test(allow_queries, deny_queries)

        def has_object_permission(self, request, view, obj):
            allow_queries, deny_queries, user_permissions = self.get_parameters(request, view, obj)

            def test(queries, reference, strict=True):
                return reduce(lambda t, p: t or match_any(p, reference, strict=strict), queries, False)

            return test(allow_queries, user_permissions) and not test(allow_queries, deny_queries)

    return TriadPermission
