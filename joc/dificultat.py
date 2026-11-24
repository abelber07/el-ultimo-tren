"""Els nivells de dificultat. Es trien al menú i es guarden a les opcions.

vida: cors de la viatgera · enemics: multiplicador de quants n'hi ha · nit: segons reals per minut del rellotge ·
agressio: velocitat i pressa dels enemics · vida_enemics: cops de més que aguanten · preus: multiplicador.
"""
DIFICULTATS = {
    "facil": {"nom": "Tranquila", "desc": "Más vida, menos pasajeros y una noche más larga.",
              "vida": 7, "enemics": 0.7, "nit": 7, "agressio": 0.8, "vida_enemics": 0, "preus": 0.75,
              "vida_jefe": 0.7},
    "normal": {"nom": "Normal", "desc": "El viaje tal como es.",
               "vida": 5, "enemics": 1.0, "nit": 5, "agressio": 1.0, "vida_enemics": 0, "preus": 1.0,
               "vida_jefe": 1.0},
    "dificil": {"nom": "Pesadilla", "desc": "Menos vida, más pasajeros, más rápidos y una noche corta.",
                "vida": 4, "enemics": 1.35, "nit": 4, "agressio": 1.25, "vida_enemics": 1, "preus": 1.25,
                "vida_jefe": 1.3},
}
ORDRE = ["facil", "normal", "dificil"]


def dades(nom):
    return DIFICULTATS.get(nom, DIFICULTATS["normal"])


def seguent(nom, pas=1):
    i = ORDRE.index(nom) if nom in ORDRE else 1
    return ORDRE[(i + pas) % len(ORDRE)]
