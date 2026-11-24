"""Captures del joc sense finestra, amb un guió de tecles, per revisar com es veu.

    python tools/captures.py carpeta_sortida [escena ...]

Escenes: intro, titol, inici, segona, sostre, tunel, combat, frenada, jefe, estacio, final.
"""
import os
import sys

os.environ["JOC_FINESTRA"] = "0"
os.environ.setdefault("JOC_DADES", os.path.join(os.environ.get("TEMP", "/tmp"), "ultimo_tren_captures"))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame  # noqa: E402

import main  # noqa: E402
from joc.mon import SOSTRE_Y, TERRA_Y  # noqa: E402
from joc.partida import Partida  # noqa: E402
from motor.control import CONTROL  # noqa: E402

SORTIDA = sys.argv[1] if len(sys.argv) > 1 else "captures"
os.makedirs(SORTIDA, exist_ok=True)
joc = main.Joc()


def guardar(nom, escala=2):
    j = joc.partida.jugador if joc.partida else None
    if j and j.invul > 1000:
        j.invul = 8000                      # que no surti en el fotograma que parpelleja
    joc.dibuixar()
    pygame.image.save(pygame.transform.scale_by(joc.llenc, escala), os.path.join(SORTIDA, nom + ".png"))
    print("captura", nom)


def pas(n=1, tecles=(), prem=()):
    for i in range(n):
        CONTROL.començar()
        CONTROL.aguant = set(tecles)
        if i == 0:
            CONTROL.ara = set(prem) | set(tecles)
        joc.actualitzar()


def nova(llavor=11, dificultat="normal"):
    joc.partida = Partida(joc.atles, joc.atr, llavor=llavor, paisatge=joc.paisatge, dificultat=dificultat)
    joc.estat = "joc"
    return joc.partida


def teleport(p, vago, dx=80, y=TERRA_Y):
    v = p.tren.vagons[vago]
    j = p.jugador
    j.x, j.y = v.x0 + dx, y
    j.canviar("normal")
    p.camera(immediata=True)
    return v


escenes = sys.argv[2:] or ["intro", "titol", "inici", "segona", "sostre", "tunel", "combat", "frenada", "jefe", "estacio", "pausa", "final"]
if "intro" in escenes:
    joc.veure_intro()
    fet = 0
    for i, t in enumerate((120, 380, 520, 700, 900, 1100, 1350)):
        pas(t - fet)
        fet = t
        guardar(f"00_intro{i}")
if "titol" in escenes:
    joc.anar_titol()
    pas(60)
    guardar("01_titol")
    pas(1, prem=["avall"])
    pas(20)
    guardar("01_titol_dificultat")
    pas(1, prem=["dre"])
    pas(1, prem=["avall"])
    pas(1, prem=["avall"])
    pas(1, prem=["acceptar"])
    pas(10)
    guardar("01_controls")
    pas(1, prem=["acceptar"])
if "inici" in escenes:
    p = nova()
    pas(20)
    guardar("02_desperta")
    pas(100)
    pas(60, tecles=["dre"])
    guardar("03_cua")
if "segona" in escenes:
    p = nova()
    print([v.tipus for v in p.tren.vagons])
    for i, v in enumerate(p.tren.vagons):
        teleport(p, i, dx=60)
        p.jugador.invul = 9999
        pas(2)
        guardar(f"04_vago{i}_{v.tipus}")
        teleport(p, i, dx=v.ample // 2 + 120)
        pas(2)
        guardar(f"04_vago{i}_{v.tipus}_b")
if "sostre" in escenes:
    p = nova()
    v = p.tren.vagons[0]
    ex = v.escotilles[0]
    teleport(p, 0, dx=ex - v.x0)
    pas(1, tecles=["amunt"])
    pas(40, tecles=["amunt"])
    guardar("05_escala")
    pas(90, tecles=["amunt"])
    pas(100, tecles=["dre"])
    guardar("06_sostre")
if "tunel" in escenes:
    p = nova()
    v = teleport(p, 2, dx=200, y=SOSTRE_Y)
    p.jugador.invul = 0
    p.esdeveniments.llançar("tunel")
    e = p.esdeveniments
    while e.avis_tunel(p.jugador.x) is None:
        pas(1)
    pas(40)
    guardar("07_tunel_avis")
    pas(1, tecles=["avall"])
    while not e.tunel_a(p.jugador.x):
        pas(1, tecles=["avall"])
    pas(30, tecles=["avall"])
    guardar("08_tunel_sostre")
    teleport(p, 2, dx=300)
    pas(10)
    guardar("09_tunel_dins")
if "combat" in escenes:
    p = nova(5)
    idx = next(i for i, v in enumerate(p.tren.vagons) if v.tipus in ("segona", "restaurant"))
    teleport(p, idx, dx=60)
    p.jugador.invul = 9999
    pas(80, tecles=["dre"])
    guardar("10_combat_a")
    for k in range(6):
        pas(8, prem=["cop"])
    guardar("11_combat_b")
    pas(1, tecles=["para"])
    pas(25, tecles=["para"])
    guardar("12_para")
    p.esdeveniments.llançar("corba")
    pas(160)
    guardar("13_corba")
if "frenada" in escenes:
    p = nova(5)
    teleport(p, 1, dx=120)
    p.jugador.invul = 9999
    p.esdeveniments.llançar("frenada")
    pas(60)
    guardar("14_frenada_avis")
    pas(54)
    guardar("14_frenada_cop")
    pas(12)
    guardar("14_frenada_b")
    p = nova(5)
    teleport(p, 1, dx=120)
    p.jugador.invul = 9999
    p.esdeveniments.llançar("frenada")
    pas(1, tecles=["avall"])
    pas(125, tecles=["avall"])
    guardar("14_frenada_agafada")
if "jefe" in escenes:
    p = nova(3)
    idx = len(p.tren.vagons) - 1
    teleport(p, idx, dx=160)
    j = p.jugador
    j.invul = 9999
    rv = next(e for e in p.enemics if getattr(e, "es_jefe", False))
    pas(30)
    guardar("16_jefe_presenta")
    pas(100)
    j.x = rv.x - 50
    while rv.estat != "alça":
        pas(1)
    pas(25)
    guardar("17_jefe_alca")
    while rv.estat != "cop":
        pas(1)
    pas(8)
    guardar("18_jefe_cop")
    pas(20)
    guardar("18_jefe_ona")
    rv.canviar("camina")
    rv.rebre(p, rv.vida - rv.vida_inicial // 2, j.x)
    pas(80)
    guardar("19_jefe_fosc")
    rv.canviar("camina")
    j.x = rv.x - 300
    rv.espera = 0
    for _ in range(600):
        if rv.estat == "estira" and rv.t > 30:
            break
        pas(1)
    guardar("20_jefe_estira")
    rv.vida = 1
    rv.canviar("encallat")
    rv.rebre(p, 1, j.x)
    pas(40)
    guardar("21_jefe_vencut")
if "estacio" in escenes:
    from joc.estacio import Estacio
    p = nova(4)
    p.jugador.bitllets = 6
    p.jugador.vida = 3
    joc.estacio = Estacio(p, joc.paisatge, joc.atles, joc.atr)
    joc.estat = "estacio"
    pas(60)
    guardar("22_estacio")
    pas(1, prem=["avall"])
    pas(10)
    guardar("22_estacio_via")
    for via in joc.estacio.vies:
        joc.partida = Partida(joc.atles, joc.atr, llavor=p.llavor_nit, paisatge=joc.paisatge, tram=2, ruta=via,
                              anterior=p)
        joc.estat = "joc"
        pas(60)
        pas(80, tecles=["dre"])
        guardar(f"23_tram2_{via}")
if "barrera" in escenes:
    p = nova(11)
    v = p.tren.vagons[1]
    teleport(p, 1, dx=v.x1 - v.x0 - 120, y=SOSTRE_Y)
    p.jugador.invul = 10 ** 6
    pas(70, tecles=["dre"])
    p.rotul = None
    pas(200)
    pas(10, tecles=["dre"])
    guardar("06_barrera")
if "pausa" in escenes:
    nova()
    pas(120, tecles=["dre"])
    joc.estat = "pausa"
    joc.menu = 0
    pas(1, prem=["avall"])
    pas(20)
    guardar("02_pausa")
if "final" in escenes:
    p = nova()
    p.jugador.vida = 0
    p.jugador.canviar("mort")
    pas(110)
    pas(60)
    guardar("15_final")
