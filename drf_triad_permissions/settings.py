import re

from django.conf import settings

TRIAD_DIVIDER = "::"
NON_STRICT_PLACEHOLDER = "some"

DEFAULT_WILDCARDS = {
    "*": r"^.+$",
    "all": r"^.+$",
    "read": r"^head|options|get|list|retrieve$",
    "write": r"^post|put|patch|delete|create|update|partial-update|destroy$",
}
CUSTOM_WILDCARDS = getattr(settings, "TRIAD_WILDCARDS", {})
WILDCARDS = {**DEFAULT_WILDCARDS, **{k: r"^" + r"|".join(v) + r"$" for k, v in CUSTOM_WILDCARDS.items()}}

COMPILED_WILDCARDS = {wildcard: re.compile(regex) for wildcard, regex in WILDCARDS.items()}

TRIAD_USER_PERMISSIONS_FUNCTION = getattr(settings, "TRIAD_USER_PERMISSIONS_FUNCTION", "get_permissions")
