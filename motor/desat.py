"""Opcions i rècords que es guarden entre partides.

A l'escriptori, un JSON a la carpeta d'usuari (%APPDATA%/ElUltimoTren o ~/.el_ultimo_tren); al navegador, el
localStorage. Amb la variable JOC_DADES es pot fer servir una altra carpeta (proves).
"""
import json
import os

from motor.nucli import WEB

CLAU = "el_ultimo_tren"
INICIAL = {"dificultat": "normal", "millor": None, "intro_vista": False}


def _carpeta():
    if os.environ.get("JOC_DADES"):
        return os.environ["JOC_DADES"]
    base = os.environ.get("APPDATA")
    if base:
        return os.path.join(base, "ElUltimoTren")
    return os.path.join(os.path.expanduser("~"), ".el_ultimo_tren")


def _fitxer():
    return os.path.join(_carpeta(), "dades.json")


def carregar():
    dades = dict(INICIAL)
    try:
        if WEB:
            import platform
            txt = platform.window.localStorage.getItem(CLAU)
            if txt:
                dades.update(json.loads(str(txt)))
        elif os.path.exists(_fitxer()):
            with open(_fitxer(), encoding="utf-8") as fh:
                dades.update(json.load(fh))
    except Exception:                       # unes dades fetes malbé no han d'impedir jugar
        pass
    return dades


def desar(dades):
    txt = json.dumps(dades, ensure_ascii=False)
    try:
        if WEB:
            import platform
            platform.window.localStorage.setItem(CLAU, txt)
        else:
            os.makedirs(_carpeta(), exist_ok=True)
            tmp = _fitxer() + ".tmp"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(txt)
            os.replace(tmp, _fitxer())
    except Exception:
        pass
