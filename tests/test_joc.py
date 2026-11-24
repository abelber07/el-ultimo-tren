"""Proves del joc sense finestra: el tren, la física, el combat, els túnels i un bot que fa tot el tram."""
import os
import sys

os.environ["JOC_FINESTRA"] = "0"
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import pygame  # noqa: E402
import pytest  # noqa: E402

from motor.nucli import Pantalla  # noqa: E402

pygame.init()
PANTALLA = Pantalla()

from joc import enemics  # noqa: E402
from joc.mon import PARET, SOSTRE_Y, TERRA_Y  # noqa: E402
from joc.partida import Partida  # noqa: E402
from joc.tren import Tren  # noqa: E402
from motor.control import CONTROL  # noqa: E402
from motor.dibuix import Atles  # noqa: E402

ATLES = Atles("personatges")
ATR = Atles("atrezzo")
ATR.afegir(ATLES, ["maleta"])


def partida(llavor=3):
    return Partida(ATLES, ATR, llavor=llavor)


def tecles(aguant=(), prem=()):
    CONTROL.començar()
    CONTROL.aguant = set(aguant)
    CONTROL.ara = set(prem)


def test_trens_ben_formats():
    for llavor in range(40):
        t = Tren(llavor)
        assert t.vagons[0].tipus == "cua"
        assert "venedor" in [v.tipus for v in t.vagons]
        tipus = [v.tipus for v in t.vagons]
        assert all(a != b for a, b in zip(tipus, tipus[1:]))
        for v in t.vagons:
            for ex in v.escotilles:
                assert v.x0 + PARET + 14 < ex < v.x1 - PARET - 14
            for e in v.spawns:
                assert v.x0 < e[1] < v.x1
            for p in v.plats:
                assert p.top < TERRA_Y


def test_es_dibuixa_sense_errors():
    p = partida()
    s = pygame.Surface((640, 360))
    for _ in range(5):
        tecles()
        p.actualitzar()
        p.dibuixar(s)


def test_pujar_al_sostre_i_baixar():
    p = partida()
    v = p.tren.vagons[0]
    j = p.jugador
    j.canviar("normal")
    j.x, j.y = v.escotilles[0], TERRA_Y
    for _ in range(200):
        tecles(["amunt"])
        p.actualitzar()
    assert j.y == SOSTRE_Y and j.estat == "normal"
    for _ in range(10):
        tecles(["dre"])
        p.actualitzar()
    assert j.y == SOSTRE_Y                       # camina pel sostre sense caure
    j.x = v.escotilles[0]
    for _ in range(200):
        tecles(["avall"])
        p.actualitzar()
    assert j.y == TERRA_Y


def test_tunel_fa_mal_dret_i_no_ajupit():
    for ajupit in (False, True):
        p = partida()
        j = p.jugador
        j.canviar("normal")
        v = p.tren.vagons[2]
        j.x, j.y = v.x0 + 200, SOSTRE_Y
        p.esdeveniments.llançar("tunel")
        vida = j.vida
        for _ in range(1000):
            tecles(["avall"] if ajupit else [])
            p.actualitzar()
        assert (j.vida == vida) == ajupit


def test_parada_perfecta_atordeix():
    p = partida()
    j = p.jugador
    j.canviar("normal")
    v = p.tren.vagons[0]
    j.x, j.y = v.x0 + 200, TERRA_Y
    j.dir = 1
    e = enemics.SenseCara(j.x + 24, TERRA_Y, 0)
    e.dir = -1
    p.enemics.append(e)
    e.canviar("prepara")
    e.t = 24
    tecles(prem=["para"])
    p.actualitzar()
    for _ in range(12):
        tecles(["para"])
        p.actualitzar()
    assert e.atordit > 0
    assert j.vida == j.vida_max


def test_cops_maten():
    p = partida()
    j = p.jugador
    j.canviar("normal")
    v = p.tren.vagons[0]
    j.x, j.y = v.x0 + 200, TERRA_Y
    j.dir = 1
    j.invul = 10000
    e = enemics.SenseCara(j.x + 22, TERRA_Y, 0)
    p.enemics.append(e)
    for i in range(200):
        tecles(prem=["cop"] if i % 6 == 0 else [])
        p.actualitzar()
        if e.mort:
            break
    assert e.mort
    assert j.bitllets >= 0


def bot(p, maxim=30000):
    """Avança cap a la dreta, pega quan hi ha algú a prop, salta si s'encalla i agafa el que troba."""
    j = p.jugador
    j.invul = 10 ** 9
    quiet = 0
    salt_fins = 0
    xant = j.x
    for f in range(maxim):
        prem, aguant = set(), {"dre"}
        davant = [e for e in p.enemics if not e.mort and e.despert() and abs(e.x - j.x) < 46
                  and abs(e.y - j.y) < 40]
        if davant:
            e = davant[0]
            aguant = {"dre"} if e.x > j.x else {"esq"}
            if f % 5 == 0:
                prem.add("cop")
        if abs(j.x - xant) < 3:                    # no avança (encara que tremoli contra una paret)
            quiet += 1
        else:
            quiet = 0
            xant = j.x
        if quiet > 25:
            v = p.tren.vagons[p.vago_actual]
            if not v.oberta:                       # porta tancada: busca qui la manté tancada
                vius = [e for e in p.enemics if e.compta() and e.vago == v.idx]
                if vius:
                    e = min(vius, key=lambda e: abs(e.x - j.x))
                    aguant = {"dre"} if e.x > j.x else {"esq"}
            if f % 20 == 0:
                prem.add("salt")
        if "salt" in prem:
            salt_fins = f + 16
        if f < salt_fins:
            aguant.add("salt")
        tecles(aguant, prem)
        p.actualitzar()
        if p.acabada:
            return f
    return None


@pytest.mark.parametrize("llavor", [1, 2, 3, 4])
def test_bot_arriba_al_final(llavor):
    p = partida(llavor)
    f = bot(p)
    assert p.acabada == "tram", (p.vago_actual, p.jugador.x)
    assert f is not None


@pytest.mark.parametrize("dif", ["facil", "dificil"])
def test_bot_arriba_amb_cada_dificultat(dif):
    for llavor in (1, 2):
        p = Partida(ATLES, ATR, llavor=llavor, dificultat=dif)
        bot(p)
        assert p.acabada == "tram", (dif, llavor, p.vago_actual, p.jugador.x)


def test_dificultat_canvia_la_partida():
    facil = Partida(ATLES, ATR, llavor=7, dificultat="facil")
    dificil = Partida(ATLES, ATR, llavor=7, dificultat="dificil")
    assert facil.jugador.vida_max > dificil.jugador.vida_max
    assert len(facil.enemics) < len(dificil.enemics)
    for _ in range(600):
        facil.esdeveniments.temps += 1
        dificil.esdeveniments.temps += 1
    assert facil.esdeveniments.minuts() < dificil.esdeveniments.minuts()


def test_agafada_no_surt_disparada_a_la_frenada():
    def recorregut(ajupida):
        p = partida(5)
        v = p.tren.vagons[1]
        j = p.jugador
        j.x, j.y = v.x0 + 120, TERRA_Y
        j.canviar("normal")
        j.invul = 10 ** 9
        p.esdeveniments.llançar("frenada")
        x0 = j.x
        for _ in range(170):
            tecles({"avall"} if ajupida else set())
            p.actualitzar()
        return j.x - x0
    assert recorregut(False) > 60
    assert recorregut(True) < 25


def test_desat_i_menu(tmp_path, monkeypatch):
    monkeypatch.setenv("JOC_DADES", str(tmp_path))
    from motor import desat
    d = desat.carregar()
    assert d["dificultat"] == "normal" and not d["intro_vista"]
    d["dificultat"] = "dificil"
    desat.desar(d)
    assert desat.carregar()["dificultat"] == "dificil"


def test_intro_i_menu_porten_al_joc(tmp_path, monkeypatch):
    monkeypatch.setenv("JOC_DADES", str(tmp_path))
    import main
    joc = main.Joc()
    assert joc.estat == "intro"
    for _ in range(1600):
        tecles()
        joc.actualitzar()
        if joc.t % 97 == 0:
            joc.dibuixar()
    assert joc.estat == "titol"
    joc.dibuixar()
    tecles(prem={"avall"})
    joc.actualitzar()
    tecles(prem={"dre"})
    joc.actualitzar()
    assert joc.dades["dificultat"] == "dificil"
    tecles(prem={"amunt"})
    joc.actualitzar()
    tecles(prem={"acceptar"})
    joc.actualitzar()
    assert joc.estat == "joc" and joc.partida.nom_dificultat == "dificil"
    joc2 = main.Joc()                       # la segona vegada ja no surt la intro
    assert joc2.estat == "titol"
