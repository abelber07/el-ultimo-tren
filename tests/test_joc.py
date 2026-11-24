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


def _jefe(llavor=3, dificultat="normal"):
    p = Partida(ATLES, ATR, llavor=llavor, dificultat=dificultat)
    v = p.tren.vagons[-1]
    assert v.tipus == "revisor"
    j = p.jugador
    j.x, j.y = v.x0 + 200, TERRA_Y
    j.canviar("normal")
    p.camera(immediata=True)
    rv = next(e for e in p.enemics if getattr(e, "es_jefe", False))
    return p, j, rv


def test_revisor_es_presenta_i_la_porta_no_obre_fins_que_cau():
    p, j, rv = _jefe()
    for _ in range(5):
        tecles()
        p.actualitzar()
    assert rv.estat == "presenta" and p.jefe is rv
    assert not p.tren.vagons[-1].oberta
    rv.canviar("encallat")
    while not rv.mort:
        rv.rebre(p, 1, j.x)
        if rv.estat == "fase2":
            assert p.jefe_fosc
            rv.canviar("encallat")
    tecles()
    p.actualitzar()
    assert rv.estat == "vençut" and not p.jefe_fosc
    for _ in range(40):
        tecles()
        p.actualitzar()
    assert p.tren.vagons[-1].oberta


def test_revisor_parada_perfecta_i_ona():
    p, j, rv = _jefe()
    j.invul = 0
    rv.canviar("camina")
    rv.vida_inicial = rv.vida
    j.x = rv.x - 40
    j.dir = 1
    while not (rv.estat == "alça" and rv.t >= 32):
        tecles()
        p.actualitzar()
    tecles(prem={"para"}, aguant={"para"})
    p.actualitzar()
    for _ in range(12):
        tecles(aguant={"para"})
        p.actualitzar()
    assert rv.estat == "atordit"
    assert j.vida == j.vida_max
    assert not p.perills, "una parada perfecta talla el cop abans de l'ona"
    rv.atordit = 0
    rv.canviar("alça")
    j.invul = 10 ** 9
    while rv.estat != "encallat":
        tecles()
        p.actualitzar()
    assert p.perills, "sense parar, la perforadora fa una ona"


def test_revisor_agafa_i_pren_bitllets():
    p, j, rv = _jefe()
    j.invul = 0
    j.bitllets = 5
    rv.canviar("estira")
    rv.vida_inicial = rv.vida
    rv.dir = -1
    j.x = rv.x - 120
    for _ in range(80):
        tecles()
        p.actualitzar()
        if rv.estat == "agafa":
            break
    assert rv.estat == "agafa" and j.bitllets == 3


@pytest.mark.parametrize("via", ["muntanya", "riu", "rapida"])
def test_segon_tram_per_cada_via(via):
    p1 = partida(2)
    bot(p1)
    assert p1.acabada == "tram"
    p1.jugador.bitllets = 7
    p2 = Partida(ATLES, ATR, llavor=p1.llavor_nit, tram=2, ruta=via, anterior=p1)
    assert p2.tram == 2 and p2.jugador.bitllets == 7
    assert p2.esdeveniments.temps == p1.esdeveniments.temps
    assert all(v.tipus != "revisor" for v in p2.tren.vagons)
    assert len(p2.tren.vagons) == (5 if via == "rapida" else 7)
    assert (p2.boira is not None) == (via == "riu")
    p2.dibuixar(PANTALLA.llenc)
    bot(p2)
    assert p2.acabada == "tram", (via, p2.vago_actual)


def test_estacio_fonda_i_via(tmp_path, monkeypatch):
    monkeypatch.setenv("JOC_DADES", str(tmp_path))
    import main
    from joc.estacio import Estacio
    joc = main.Joc()
    joc.nova_partida()
    p = joc.partida
    p.acabada = "tram"
    tecles()
    p.acabada = None
    p.jugador.x = p.tren.vagons[-1].x1 + 40
    p.tren.vagons[-1].oberta = True
    for e in p.enemics:
        e.mort = True
    for _ in range(3):
        tecles()
        joc.actualitzar()
    assert joc.estat == "estacio" and isinstance(joc.estacio, Estacio)
    est = joc.estacio
    j = p.jugador
    j.vida, j.bitllets = 2, 5
    est.sel = 0
    est.acceptar()
    assert j.vida == 4 and j.bitllets == 2 and est.descansat
    est.acceptar()
    assert j.bitllets == 2
    joc.dibuixar()
    for _ in range(40):
        tecles()
        joc.actualitzar()
    tecles(prem={"avall"})
    joc.actualitzar()
    tecles(prem={"acceptar"})
    joc.actualitzar()
    assert joc.estat == "joc" and joc.partida.tram == 2
    assert joc.partida.jugador.bitllets == 2


def test_pel_sostre_no_es_pot_saltar_un_vago_tancat():
    p = partida(3)
    v = p.tren.vagons[1]
    e = enemics.SenseCara(v.x0 + 100, TERRA_Y, 1)
    p.enemics.append(e)
    p._actualitzar_portes()
    assert not v.oberta
    j = p.jugador
    j.canviar("normal")
    j.x, j.y = v.x1 - 200, SOSTRE_Y
    j.invul = 10 ** 9
    e.canviar("quiet")
    for f in range(300):
        tecles({"dre"} | ({"salt"} if f % 30 < 16 else set()), {"salt"} if f % 30 == 0 else set())
        p.actualitzar()
    assert j.x < v.x1, "ha passat per dalt d'un vagó amb la porta tancada"


def test_menu_amb_el_ratoli(tmp_path, monkeypatch):
    monkeypatch.setenv("JOC_DADES", str(tmp_path))
    import main
    joc = main.Joc()
    joc.anar_titol()
    tecles()
    joc.t = 20
    joc.dibuixar()                            # calcula on és cada opció
    joc.ratoli = joc.rects[2].center
    tecles()
    joc.actualitzar()
    assert joc.menu == 2
    joc.dibuixar()
    joc.clic = joc.ratoli = joc.rects[0].center
    tecles()
    joc.actualitzar()
    assert joc.estat == "joc"
