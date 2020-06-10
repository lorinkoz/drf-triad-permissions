import re

from django.conf import settings

DEFAULT_TRIAD_WILDCARDS = {
    "*": r"^.+$",
    "all": r"^.+$",
    "[read]": r"^list|retrieve$",
    "read": r"^list|retrieve$",
    "[write]": r"^create|update|partial-update|destroy$",
    "write": r"^create|update|partial-update|destroy$",
}

TRIAD_DIVIDER = getattr(settings, "TRIAD_DIVIDER", "::")
TRIAD_SOFT_WILDCARD = getattr(settings, "TRIAD_SOFT_WILDCARD", "some")
TRIAD_WILDCARDS = {
    **DEFAULT_TRIAD_WILDCARDS,
    **getattr(settings, "TRIAD_WILDCARDS", dict()),
}

TRIAD_USER_PERMISSIONS_FUNCTION = getattr(settings, "TRIAD_USER_PERMISSIONS_FUNCTION", "get_permissions")

TRIAD_COMPILED_WILDCARDS = {wildcard: re.compile(regex) for wildcard, regex in TRIAD_WILDCARDS.items()}

DEFAULT_TRIAD_PLACEHOLDERS = {
    "action": lambda request, view, obj=None: view.action.replace("_", "-"),
    "resource": lambda request, view, obj=None: getattr(
        view, "permissions_resource", getattr(view, "basename", TRIAD_SOFT_WILDCARD)
    ),
    "id": lambda request, view, obj=None: (f"id:{obj.permissions_id}" if obj else TRIAD_SOFT_WILDCARD),
    "owner": lambda request, view, obj=None: (f"owner:{obj.permissions_owner}" if obj else TRIAD_SOFT_WILDCARD),
}

TRIAD_PLACEHOLDERS = {
    **DEFAULT_TRIAD_PLACEHOLDERS,
    **getattr(settings, "TRIAD_PLACEHOLDERS", dict()),
}
