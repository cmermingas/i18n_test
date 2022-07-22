from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.utils import translation
from django.conf import settings


def index(request):
    # (1) Activate (change code below): de-be, es-mx
    # (2) Test django.po translations @ http://127.0.0.1:8000/test/
    # (3) Test djangojs.po translations @ http://127.0.0.1:8000/jsi18n/

    translation.activate('es-mx')  # <--- Activate de-be, es-mx here (can also try with de, es, en)
    strings = {
        "get_language()": translation.get_language(),
        "en - Not translated": _("en - Not translated"),
        "de - Not translated": _("de - Not translated"),
        "de_BE - Not translated": _("de_BE - Not translated"),
        "es - Not translated": _("es - Not translated"),
        "es_MX - Not translated": _("es_MX - Not translated"),
    }
    response = JsonResponse(strings)
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, translation.get_language())
    return response
