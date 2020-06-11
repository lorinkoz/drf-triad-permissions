from django.http import HttpResponse
from django.template.loader import render_to_string

from .settings import NON_STRICT_PLACEHOLDER, TRIAD_DIVIDER, WILDCARDS


def triad_permissions_js(request):
    body = render_to_string(
        "drf_triad_permissions/code.js.tpl",
        context={
            "NON_STRICT_PLACEHOLDER": NON_STRICT_PLACEHOLDER,
            "TRIAD_DIVIDER": TRIAD_DIVIDER,
            "WILDCARDS": WILDCARDS,
        },
    )
    return HttpResponse(body, content_type="application/javascript")
