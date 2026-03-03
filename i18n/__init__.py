"""Internationalization support for TmuxPlus.

Usage:
    from i18n import t, set_locale

    set_locale("pt_BR")   # call before importing app modules
    print(t("Sessions"))  # "Sessões"

The default locale is English — keys are the English strings themselves,
so missing translations fall back gracefully to readable English.

Adding a new locale:
    1. Create i18n/<locale_code>.py with a STRINGS dict.
    2. Call set_locale("<locale_code>") in main.py.
"""

_translations: dict[str, str] = {}


def set_locale(locale_code: str) -> None:
    """Load translations for the given locale code (e.g. 'pt_BR')."""
    global _translations
    try:
        import importlib
        module = importlib.import_module(f"i18n.{locale_code}")
        _translations = module.STRINGS
    except (ImportError, AttributeError):
        _translations = {}


def t(key: str, default: str | None = None) -> str:
    """Return the translation for key, or default, or the key itself (English)."""
    if key in _translations:
        return _translations[key]
    return default if default is not None else key
