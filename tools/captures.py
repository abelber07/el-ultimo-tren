"""Captures del joc sense finestra, amb un guió de tecles, per revisar com es veu.

    python tools/captures.py carpeta_sortida [escena ...]

Escenes: titol, inici, segona, sostre, tunel, combat, final.
"""
import os
import sys

os.environ["JOC_FINESTRA"] = "0"
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


def nova(llavor=11):
    joc.partida = Partida(joc.atles, joc.atr, llavor=llavor, paisatge=joc.paisatge)
    joc.estat = "joc"
    return joc.partida


def teleport(p, vago, dx=80, y=TERRA_Y):
    v = p.tren.vagons[vago]
    j = p.jugador
    j.x, j.y = v.x0 + dx, y
    j.canviar("normal")
    p.camera(immediata=True)
    return v


escenes = sys.argv[2:] or ["titol", "inici", "segona", "sostre", "tunel", "combat", "final"]
if "titol" in escenes:
    joc.estat = "titol"
    for _ in range(30):
        joc.actualitzar()
    guardar("01_titol")
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
    p.esdeveniments.llançar("frenada")
    pas(120)
    guardar("14_frenada")
if "final" in escenes:
    p = nova()
    p.jugador.vida = 0
    p.jugador.canviar("mort")
    pas(110)
    pas(60)
    guardar("15_final")
