import os
import logging
from jinja2 import Environment, FileSystemLoader
from babel.support import Translations
from user_prompts import show_error

logger = logging.getLogger(__name__)

def crea_ambiente_jinja(lang: str = "it_IT"):
    """
    Crea un ambiente Jinja2 con supporto per localizzazione.
    Se non trova file di traduzione, usa un fallback identitario.
    """
    loader = FileSystemLoader("docs")
    env = Environment(loader=loader, extensions=["jinja2.ext.i18n"])
    path_mo = os.path.join("locales", lang, "LC_MESSAGES", "messages.mo")
    if os.path.exists(path_mo):
        try:
            with open(path_mo, "rb") as f:
                translations = Translations(f)
            env.install_gettext_translations(translations, newstyle=True)
            logger.info("[OK] Traduzioni caricate da: %s", path_mo)
        except Exception as e:
            show_error(f"Errore nel caricamento traduzioni: {e}", level="warning", log_only=True)
            env.globals.update(_=lambda x: x)
    else:
        logger.info(f"ℹ️ Nessun file di traduzione trovato per {lang}. Uso fallback.")
        env.globals.update(_=lambda x: x)
    return env


def render_template(template_dir: str, template_name: str, context: dict):
    """
    API minima: renderizza un template Jinja2 con un contesto.
    """
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    return template.render(context)
