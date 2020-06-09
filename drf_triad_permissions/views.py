from django.http import HttpResponse

from .settings import TRIAD_DIVIDER, TRIAD_WILDCARDS


def triad_permissions_js(request):
    body = render_to_string(
        "triad_permissions/code.js.tpl",
        context={
            "TRIAD_DIVIDER": TRIAD_DIVIDER,
            "TRIAD_SOFT_WILDCARD": TRIAD_SOFT_WILDCARD,
            "TRIAD_WILDCARDS": TRIAD_WILDCARDS,
        },
    )
    return HttpResponse(body, content_type="application/javascript")
