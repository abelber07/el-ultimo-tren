"""Les vies que es poden triar a l'estació entre tram i tram. Cadascuna canvia com és el tram següent.

vagons: quants n'hi ha · pesos: probabilitat de túnel, frenada i corba · interval: segons entre esdeveniments ·
boira: es veu poc lluny · bitllets: multiplicador dels que es troben · premi: què et dona en triar-la.
"""
import random

RUTES = {
    "muntanya": {"nom": "Vía de las Montañas", "desc": "Muchos túneles y curvas cerradas.",
                 "premi_txt": "Al subir: +1 corazón máximo", "premi": "cor",
                 "vagons": 7, "pesos": (0.6, 0.1, 0.3), "interval": (18, 30), "boira": False, "bitllets": 1.0},
    "riu": {"nom": "Vía del Río", "desc": "Niebla espesa: apenas se ve nada.",
            "premi_txt": "Más billetes en cada vagón", "premi": None,
            "vagons": 7, "pesos": (0.35, 0.25, 0.4), "interval": (22, 38), "boira": True, "bitllets": 2.0},
    "rapida": {"nom": "Vía Rápida", "desc": "Solo cinco vagones, pero frena sin parar.",
               "premi_txt": "Llegas antes a la locomotora", "premi": None,
               "vagons": 5, "pesos": (0.2, 0.6, 0.2), "interval": (14, 24), "boira": False, "bitllets": 1.0},
}
NORMAL = {"nom": "", "vagons": 7, "pesos": (0.45, 0.25, 0.3), "interval": (22, 38), "boira": False, "bitllets": 1.0}


def ruta(nom):
    return RUTES.get(nom, NORMAL)


def oferta(llavor, n=2):
    """Les vies que ofereix l'estació (sempre les mateixes amb la mateixa llavor)."""
    noms = sorted(RUTES)
    random.Random(llavor * 13 + 5).shuffle(noms)
    return noms[:n]
