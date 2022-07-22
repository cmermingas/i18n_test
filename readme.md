# Issue with or improper use of Django JavaScriptCatalog?

I created this test app to troubleshoot a problem we are having with Django's `JavaScriptCatalog`.

## Project setup

* `LOCALE_PATHS` set to `PROJECT_ROOT/locale`.
* Translations for all apps stored under `LOCALE_PATHS`.
* `JavaScriptCatalog` configured without `packages`:

    ```
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog')
    ```

* Translations in the project (`django` and `djangojs` domains):
  * `es_MX` and `es` (demonstrate the problem).
  * `de_BE` and `de` (don't demonstrate the problem).
* Test view with four strings, each one translated in a specific `po` file:

    ```
    strings = {
        "en - Not translated": _("en - Not translated"),
        "de - Not translated": _("de - Not translated"),
        "de_BE - Not translated": _("de_BE - Not translated"),
        "es - Not translated": _("es - Not translated"),
        "es_MX - Not translated": _("es_MX - Not translated"),
    }
    ```

## Issue

### Expected behavior
Translations from a region-specific language code (`es-mx`) first fall back to their base language code
(`es`) and then to the default language.

### Observed behavior
When the language is set to `es-mx`, strings that are not translated in `es_MX` appear in the JavaScript
catalog with their translations from the default language (set by `LANGUAGE_CODE`).

Note: This can happen with (some) other locale codes. I am using `es-mx` as an example.

## Test as follows

### Setup
* Set up virtualenv: `python3 -m venv .venv; . .venv/bin/activate`
* Install requirements `pip install -r requirements.txt`
* Compile messages:  `python manage.py compilemessages`
* Run server: `python manage.py runserver`

### Steps to test
1. Activate `es-mx` in the test view (edit code @ `testapp/views.py`).
2. First, visit http://127.0.0.1:8000/test/

    Notice:

    ```
    # Falls back to es/django.po: 
    "es - Not translated": "es - Translated @ es/django.po"
   
    # From es_MX/django.po
    "es_MX - Not translated": "es_MX - Translated @ es_MX/django.po" 
    ```

3. Then, visit http://127.0.0.1:8000/jsi18n/

    Notice:

    ```
    # From es_MX/djangojs.po
    "es_MX - Not translated": "es_MX - Translated @ es_MX/djangojs.po"
    
    # "es - Not translated" not present in the catalog <-- This is the issue
    # It should have been pulled from es/djangojs.po
   ```


## Observed cause

`JavaScriptCatalog` uses the first level of `fallback` from the translations
([link to code](https://github.com/django/django/blob/f81032572107846922745b68d5b7191058fdd5f5/django/views/i18n.py#L279-L281)):

    trans_fallback_cat = (
        self.translation._fallback._catalog if self.translation._fallback else {}
    )

However, in the case of `es_MX` there is a deeper chain of `fallback` objects: 

    >>> from django.utils.translation.trans_real import DjangoTranslation
    >>> dt = DjangoTranslation('es-mx', domain='djangojs')
    >>> strings = dict(dt._catalog.items())

    # es_MX translation present in _catalog as expected:
    >>> strings.get('es_MX - Not translated')  

    # Fallback es translation not present in first _fallback:
    >>> dt._fallback._catalog.get('es - Not translated')

    # Fallback es translation present in second _fallback:
    >>> dt._fallback._fallback._catalog.get('es - Not translated') 

The reason for this is that the first level of fallback comes from another app,
the admin in this specific case.


### Confirmation tests

* Repeat the test with `de-be`. It works as expected.

* Remove or rename the Django admin's files `es/LC_MESSAGES/djangojs*` and test with `es-mx`.
It works as expected.

* Configure the catalog like this: `JavaScriptCatalog.as_view(packages=['testapp'])`
and test with `es-mx`.  It works as expected.
