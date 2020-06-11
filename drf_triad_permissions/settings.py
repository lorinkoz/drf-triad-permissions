import re

from django.conf import settings


TRIAD_DIVIDER = "::"
NON_STRICT_PLACEHOLDER = "some"

WILDCARDS = {
    "*": r"^.+$",
    "all": r"^.+$",
    "read": r"^head|options|get|list|retrieve$",
    "write": r"^post|put|patch|delete|create|update|partial-update|destroy$",
}
COMPILED_WILDCARDS = {wildcard: re.compile(regex) for wildcard, regex in WILDCARDS.items()}

TRIAD_USER_PERMISSIONS_FUNCTION = getattr(settings, "TRIAD_USER_PERMISSIONS_FUNCTION", "get_permissions")
