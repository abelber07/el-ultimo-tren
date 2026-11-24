"""Genera els personatges a assets/img/personatges.png + personatges.json.

    python tools/generar_personatges.py [vista.png]

La viatgera (la protagonista) i els enemics del primer tram: el passatger sense cara, la maleta viva i el
polissó. Tots miren a la dreta (el joc els gira). El JSON guarda, per a cada fotograma, el rectangle dins
l'atles i on queda l'àncora (els peus, al mig) respecte de la cantonada de dalt a l'esquerra.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame  # noqa: E402
from pintor import Figura, comprovar_paleta, empaquetar, retallar  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
SORTIDA = os.path.join(AQUI, "..", "assets", "img")

MAT = {
    "abric": [(44, 22, 14), (116, 64, 30), (164, 100, 44), (206, 144, 70), (242, 196, 122)],
    "abric_f": [(34, 18, 12), (88, 48, 24), (124, 76, 36), (158, 108, 54), (196, 150, 92)],
    "bufanda": [(56, 10, 18), (142, 28, 38), (198, 52, 54), (234, 98, 86), (255, 162, 142)],
    "pell": [(54, 26, 22), (152, 92, 70), (208, 140, 108), (238, 186, 150), (255, 226, 198)],
    "cabell": [(18, 12, 14), (46, 30, 30), (72, 48, 44), (102, 72, 62), (142, 110, 96)],
    "gorra": [(28, 20, 16), (72, 50, 40), (100, 72, 56), (132, 100, 78), (172, 140, 112)],
    "pantalo": [(14, 14, 24), (38, 36, 54), (56, 54, 78), (80, 78, 106), (112, 110, 142)],
    "pantalo_f": [(12, 12, 20), (30, 28, 44), (44, 42, 62), (62, 60, 84), (88, 86, 112)],
    "bota": [(16, 10, 10), (48, 30, 26), (72, 46, 36), (100, 68, 52), (142, 104, 82)],
    "paraigua": [(8, 8, 14), (26, 26, 42), (42, 42, 64), (66, 64, 94), (112, 110, 152)],
    "fusta": [(42, 20, 10), (102, 58, 28), (142, 86, 42), (182, 120, 64), (222, 170, 110)],
    "metall": [(30, 30, 38), (90, 92, 106), (140, 142, 158), (190, 192, 208), (240, 240, 252)],
    # el passatger sense cara
    "vestit": [(16, 18, 24), (44, 48, 60), (64, 70, 86), (90, 98, 116), (128, 136, 156)],
    "vestit_f": [(12, 14, 18), (34, 36, 46), (50, 54, 66), (70, 76, 90), (100, 106, 122)],
    "cara": [(60, 58, 64), (150, 148, 154), (196, 194, 198), (226, 224, 226), (250, 248, 248)],
    "bombi": [(6, 6, 8), (20, 20, 24), (32, 32, 38), (50, 50, 58), (84, 84, 96)],
    "camisa": [(70, 68, 66), (164, 160, 152), (206, 202, 192), (232, 228, 218), (252, 250, 242)],
    # la maleta viva
    "cuir": [(40, 20, 12), (104, 54, 28), (146, 82, 42), (184, 116, 62), (222, 160, 100)],
    "cuir_f": [(30, 16, 10), (80, 42, 22), (112, 64, 34), (142, 90, 50), (176, 126, 80)],
    "sivella": [(60, 44, 14), (150, 112, 40), (204, 160, 62), (236, 204, 104), (255, 240, 180)],
    "boca": [(28, 4, 10), (70, 10, 20), (110, 20, 34), (150, 40, 52), (190, 76, 84)],
    "dent": [(96, 92, 80), (188, 184, 166), (226, 222, 204), (244, 242, 228), (255, 255, 246)],
    # el polissó
    "drap": [(20, 22, 14), (52, 56, 34), (76, 80, 48), (104, 108, 66), (140, 144, 96)],
    "drap_f": [(16, 16, 10), (40, 42, 26), (58, 60, 38), (80, 82, 52), (108, 110, 74)],
    "sac": [(54, 42, 26), (128, 104, 66), (170, 142, 94), (204, 180, 128), (236, 216, 170)],
    "ull": [(120, 90, 10), (220, 180, 40), (255, 222, 80), (255, 240, 150), (255, 252, 220)],
    # el Revisor
    "uniforme": [(8, 10, 24), (24, 28, 54), (36, 42, 76), (54, 62, 102), (82, 92, 136)],
    "uniforme_f": [(6, 8, 18), (18, 20, 40), (28, 32, 58), (42, 48, 80), (64, 72, 108)],
    "guant": [(90, 88, 84), (178, 174, 166), (214, 210, 202), (236, 234, 228), (252, 252, 248)],
    "llauto": [(64, 42, 12), (146, 104, 34), (200, 154, 56), (234, 198, 98), (255, 240, 178)],
    "farol": [(120, 60, 8), (226, 140, 34), (255, 196, 80), (255, 228, 150), (255, 250, 220)],
    "ombra": [(2, 2, 4), (8, 8, 12), (14, 14, 20), (22, 22, 30), (34, 34, 44)],
}
comprovar_paleta(MAT)


def pt(o, a, l):
    """Punt a distància l d'o, amb angle a des de la vertical cap avall (positiu = endavant)."""
    return (o[0] + math.sin(a) * l, o[1] + math.cos(a) * l)


# ---------------------------------------------------------------------------------------------
# La viatgera
# ---------------------------------------------------------------------------------------------
VW, VH = 56, 52            # llenç; els peus a la fila de baix, al mig (x = 28)
P_BASE = {"dx": 0, "ajup": 0, "incl": 0.0,
          "c_d": 0.0, "f_d": 0.0, "c_e": 0.0, "f_e": 0.0,                  # cuixa i flexió (davant/darrere)
          "b_d": 0.3, "a_d": -0.4, "b_e": -0.2, "a_e": -0.3,               # braç i avantbraç
          "paraigua": "tancat", "ap": 2.6,                                 # angle del paraigua des de la mà
          "vol": 0.0, "bufanda": 0.0, "gir": 0.0, "mans_amunt": False, "estirat": False}


def cama(f, mat, maluc, a, flex, llarg=7.6):
    g = pt(maluc, a, llarg)
    p = pt(g, a - flex, llarg)
    f.membre(mat, [maluc, g, p], [2.7, 2.3, 2.1])
    f.el·lipse("bota", p[0] - 2.2, p[1] - 2.6, p[0] + 3.8, p[1] + 0.6)
    return p


def braç(f, mat, esp, a1, a2, l1=6.2, l2=5.6):
    c = pt(esp, a1, l1)
    m = pt(c, a2, l2)
    f.membre(mat, [esp, c, m], [2.4, 2.1, 1.9])
    f.cercle("pell", m[0], m[1], 1.7)
    return m


def paraigua_tancat(f, ma, a, llarg=21):
    """El paraigua plegat: la nansa a la mà i la punta a `llarg` en la direcció a."""
    ux, uy = math.sin(a), math.cos(a)
    nx, ny = -uy, ux
    punta = (ma[0] + ux * llarg, ma[1] + uy * llarg)
    # nansa en ganxo (cap enrere de la punta)
    g0 = (ma[0] - ux * 2.5, ma[1] - uy * 2.5)
    f.membre("fusta", [(ma[0] + ux * 1.5, ma[1] + uy * 1.5), g0, (g0[0] + nx * 3, g0[1] + ny * 3),
                       (g0[0] + nx * 3 + ux * 1.6, g0[1] + ny * 3 + uy * 1.6)], 1.1, mode="pla")
    f.membre("metall", [(ma[0] + ux * 2, ma[1] + uy * 2), punta], 0.8, mode="pla")
    tela = []
    for k, w in ((0.22, 0.6), (0.36, 2.3), (0.6, 2.6), (0.82, 1.6), (0.9, 0.5)):
        tela.append((ma[0] + ux * llarg * k + nx * w, ma[1] + uy * llarg * k + ny * w))
    for k, w in ((0.9, 0.5), (0.82, 1.4), (0.6, 2.2), (0.36, 2.0), (0.22, 0.6)):
        tela.append((ma[0] + ux * llarg * k - nx * w, ma[1] + uy * llarg * k - ny * w))
    f.poli("paraigua", tela)
    f.linia((ma[0] + ux * llarg * 0.3, ma[1] + uy * llarg * 0.3),
            (ma[0] + ux * llarg * 0.8, ma[1] + uy * llarg * 0.8), MAT["paraigua"][3])


def paraigua_obert(f, ma):
    """Obert davant del cos com un escut: la cúpula bombada cap endavant."""
    cx, cy = ma[0] + 7, ma[1] - 2
    pts = []
    for i in range(15):
        t = -math.pi / 2 + math.pi * i / 14
        pts.append((cx + math.cos(t) * 7.5, cy + math.sin(t) * 15))
    for i in range(6, -1, -1):                       # la vora interior, ondulada entre varetes
        t = -math.pi / 2 + math.pi * i / 6
        pts.append((cx + 1.2 + math.cos(t) * 1.5, cy + math.sin(t) * 14.5))
    f.membre("fusta", [ma, (ma[0] + 3, ma[1])], 1.2, mode="pla")
    f.poli("paraigua", pts, mode="volum")
    for i in range(1, 6):
        t = -math.pi / 2 + math.pi * i / 6
        f.linia((cx + 1.5, cy + math.sin(t) * 13), (cx + math.cos(t) * 6.8, cy + math.sin(t) * 14.2),
                MAT["paraigua"][0])
    f.membre("metall", [(cx + 7, cy), (cx + 10, cy)], 0.8, mode="pla")


def viatgera(**pose):
    p = dict(P_BASE, **pose)
    f = Figura(VW, VH, MAT, brillants=("metall", "bufanda"))
    if p["gir"]:
        f.girar_tot(p["gir"], (28, 38))
    if p["estirat"]:
        return viatgera_estirada(f)
    x0 = 28 + p["dx"]
    maluc = (x0, 34.0 + p["ajup"])
    inc = p["incl"]
    coll = pt(maluc, math.pi + inc, 13 - p["ajup"] * 0.25)
    esp = (coll[0] - 0.5, coll[1] + 2.2)
    cap = (coll[0] + 1.2 + inc * 2, coll[1] - 5.2)

    # braç de darrere
    if p["mans_amunt"]:
        braç(f, "abric_f", (esp[0] - 1, esp[1]), math.pi - 0.15, math.pi + 0.15)
    else:
        braç(f, "abric_f", (esp[0] - 1, esp[1]), p["b_e"], p["a_e"])
    # cames
    cama(f, "pantalo_f", (maluc[0] - 1, maluc[1]), p["c_e"], p["f_e"])
    cama(f, "pantalo", (maluc[0] + 1, maluc[1]), p["c_d"], p["f_d"])
    # punta de la bufanda (darrere del cos)
    v = p["bufanda"]
    f.membre("bufanda", [(coll[0] - 1, coll[1] + 1), (coll[0] - 5, coll[1] + 2 + v * 0.3),
                         (coll[0] - 9 - v, coll[1] + 4 - v * 0.8)], [1.6, 1.4, 1.1], mode="pla")
    # l'abric: del coll fins a sota els genolls, obert per baix quan corre
    vol = p["vol"]
    hem_y = maluc[1] + 8.5 - p["ajup"] * 0.35
    abric = [(coll[0] - 4.2, coll[1] + 1), (coll[0] + 3.6, coll[1] + 1),
             (maluc[0] + 4.6, maluc[1] - 1), (maluc[0] + 5.2 + vol * 0.3, hem_y),
             (maluc[0] + 1, hem_y + 0.6), (maluc[0] - 4.5 - vol, hem_y - vol * 0.6),
             (maluc[0] - 4.8, maluc[1] - 2)]
    f.poli("abric", abric)
    f.marca_linia((coll[0] + 1.5, coll[1] + 3), (maluc[0] + 2.2, hem_y - 1), -1)      # la tapeta
    f.marca_linia((maluc[0] - 3.5, maluc[1] - 1), (maluc[0] + 4, maluc[1] - 1), -1)    # el cinturó
    # bufanda al coll
    f.el·lipse("bufanda", coll[0] - 4, coll[1] - 1.6, coll[0] + 4, coll[1] + 2.4)
    # el cap
    f.el·lipse("pell", cap[0] - 4.3, cap[1] - 4.6, cap[0] + 4.3, cap[1] + 4.4)
    f.poli("cabell", [(cap[0] - 4.8, cap[1] - 1.5), (cap[0] - 4.2, cap[1] + 3.8), (cap[0] - 1.8, cap[1] + 2.8),
                      (cap[0] - 1, cap[1] - 1.5)])
    f.poli("gorra", [(cap[0] - 5, cap[1] - 1.8), (cap[0] - 4.2, cap[1] - 4.8), (cap[0] - 0.5, cap[1] - 6.2),
                     (cap[0] + 3.6, cap[1] - 5), (cap[0] + 4.6, cap[1] - 2.6), (cap[0] + 7.2, cap[1] - 2),
                     (cap[0] + 7, cap[1] - 1.2), (cap[0] - 5, cap[1] - 1)])
    f.px(cap[0] + 2.4, cap[1] + 0.2, MAT["cabell"][0])                                   # l'ull
    f.px(cap[0] + 2.4, cap[1] - 0.8, MAT["cabell"][1])
    f.px(cap[0] + 4.2, cap[1] + 2.6, MAT["pell"][1])                                     # la boca
    # braç de davant i paraigua
    esp_d = (esp[0] + 0.5, esp[1] + 0.3)
    if p["mans_amunt"]:
        m = braç(f, "abric", esp_d, math.pi + 0.15, math.pi - 0.1)
    else:
        m = braç(f, "abric", esp_d, p["b_d"], p["a_d"])
    if p["paraigua"] == "tancat":
        paraigua_tancat(f, m, p["ap"])
    elif p["paraigua"] == "obert":
        paraigua_obert(f, m)
    return f


def viatgera_estirada(f):
    """Estirada a terra (caiguda o vençuda)."""
    y = 47
    cama(f, "pantalo_f", (24, y - 2), -1.5, 0.15)
    f.poli("abric", [(26, y - 6), (40, y - 6.5), (41, y), (24, y), (21, y - 3)])
    f.el·lipse("bufanda", 38, y - 7, 43, y - 2)
    f.el·lipse("pell", 41, y - 8, 49, y)
    f.poli("gorra", [(47, y - 9), (52, y - 7), (51, y - 2), (48, y - 4)])
    braç(f, "abric", (36, y - 4), -1.3, -1.6)
    paraigua_tancat(f, (30, y - 1), -1.45, llarg=19)
    return f


def cicle_cames(t, amplada=0.75):
    """Angles de cuixa i flexió per a les dues cames en el moment t (0-1) de la cursa."""
    a = math.sin(t * math.tau) * amplada
    b = math.sin(t * math.tau + math.pi) * amplada
    fd = 0.25 + max(0.0, -math.cos(t * math.tau)) * 1.1
    fe = 0.25 + max(0.0, math.cos(t * math.tau)) * 1.1
    return a, fd, b, fe


def fotogrames_viatgera():
    fs = {}
    fs["quiet0"] = viatgera()
    fs["quiet1"] = viatgera(ajup=0.6, bufanda=1.5, b_d=0.35, a_d=-0.35)
    for i in range(6):
        t = i / 6
        a, fd, b, fe = cicle_cames(t)
        bob = abs(math.sin(t * math.tau)) * -0.8
        fs[f"corre{i}"] = viatgera(c_d=a, f_d=fd, c_e=b, f_e=fe, incl=0.16, ajup=bob + 0.8, vol=2 + 1.5 * (i % 2),
                                   bufanda=3 + (i % 3), b_d=-b * 0.8 + 0.2, a_d=-0.9, b_e=-a * 0.8,
                                   a_e=-0.9, ap=2.1)
    fs["salt"] = viatgera(c_d=0.9, f_d=1.4, c_e=-0.2, f_e=0.8, vol=1.5, bufanda=-1, b_d=-0.6, a_d=-1.6, ap=2.9,
                          b_e=0.9, a_e=0.4)
    fs["caiguda"] = viatgera(c_d=0.4, f_d=0.5, c_e=-0.5, f_e=0.6, vol=-1, bufanda=-3, b_d=1.4, a_d=1.2, ap=2.6,
                             b_e=-1.6, a_e=-1.2)
    fs["ajup"] = viatgera(ajup=8, c_d=1.35, f_d=2.5, c_e=1.0, f_e=2.4, incl=0.35, vol=1, b_d=0.9, a_d=0.2,
                          ap=2.2)
    for i in range(4):
        t = i / 4
        a = math.sin(t * math.tau) * 0.3
        fs[f"sigil{i}"] = viatgera(ajup=8, c_d=1.3 + a, f_d=2.4, c_e=1.05 - a, f_e=2.4, incl=0.4, vol=1,
                                   b_d=0.9, a_d=0.2, ap=2.2, bufanda=1 + i % 2)
    for i in range(4):
        fs[f"volta{i}"] = viatgera(ajup=9, c_d=1.6, f_d=2.8, c_e=1.4, f_e=2.8, incl=0.9, b_d=1.4, a_d=1.6,
                                   b_e=1.2, a_e=1.5, ap=1.6, gir=i * math.pi / 2, bufanda=3)
    # cop amb el paraigua: preparació, cop, seguiment
    fs["cop0"] = viatgera(c_d=0.35, f_d=0.4, c_e=-0.3, f_e=0.3, incl=-0.1, b_d=2.9, a_d=3.1, ap=3.7, bufanda=1)
    fs["cop1"] = viatgera(c_d=0.5, f_d=0.4, c_e=-0.45, f_e=0.3, incl=0.25, b_d=1.75, a_d=1.6, ap=1.58,
                          bufanda=3, vol=1)
    fs["cop2"] = viatgera(c_d=0.55, f_d=0.5, c_e=-0.5, f_e=0.4, incl=0.3, b_d=0.9, a_d=0.7, ap=0.75,
                          bufanda=4, vol=2)
    # estocada (el tercer cop): el braç estirat i el paraigua recte
    fs["esto0"] = viatgera(c_d=0.3, f_d=0.6, c_e=-0.3, f_e=0.5, incl=-0.15, b_d=0.2, a_d=-1.0, ap=1.62)
    fs["esto1"] = viatgera(dx=3, c_d=0.9, f_d=0.3, c_e=-0.7, f_e=0.2, incl=0.35, b_d=1.62, a_d=1.6, ap=1.6,
                           bufanda=5, vol=3)
    fs["para"] = viatgera(c_d=0.45, f_d=0.6, c_e=-0.35, f_e=0.5, incl=0.05, b_d=1.2, a_d=1.6,
                          paraigua="obert", ajup=1)
    fs["mal"] = viatgera(c_d=-0.3, f_d=0.4, c_e=0.4, f_e=0.6, incl=-0.35, b_d=-0.9, a_d=-1.4, b_e=-1.2,
                         a_e=-1.4, ap=3.4, bufanda=-2, vol=-2)
    for i in range(2):
        s = 1 if i == 0 else -1
        fs[f"escala{i}"] = viatgera(c_d=0.6 * s + 0.2, f_d=1.0 + 0.6 * s, c_e=-0.6 * s + 0.2, f_e=1.0 - 0.6 * s,
                                    mans_amunt=True, paraigua="cap")
    fs["porta0"] = viatgera(mans_amunt=True, paraigua="cap")
    for i in range(4):
        a, fd, b, fe = cicle_cames(i / 4, 0.6)
        fs[f"portac{i}"] = viatgera(c_d=a, f_d=fd, c_e=b, f_e=fe, mans_amunt=True, paraigua="cap",
                                    vol=1 + i % 2, bufanda=2 + i % 2, ajup=0.6)
    fs["llança"] = viatgera(c_d=0.5, f_d=0.4, c_e=-0.4, f_e=0.3, incl=0.3, b_d=1.9, a_d=1.9, b_e=1.6, a_e=1.7,
                            paraigua="cap", bufanda=3, vol=1)
    fs["estirada"] = viatgera(estirat=True)
    # frenada: empesa cap on mira (s'inclina endavant i fa voltar els braços) o d'esquena (es tira enrere)
    for i in range(2):
        k = 0.35 * i
        fs[f"trontolla_d{i}"] = viatgera(c_d=0.55, f_d=0.25, c_e=-0.65, f_e=0.4, incl=0.5, b_d=-2.1 - k,
                                         a_d=-2.6 - k, b_e=-2.7 + k, a_e=-3.0 + k, ap=3.5, bufanda=-4, vol=-2)
        fs[f"trontolla_e{i}"] = viatgera(c_d=0.7, f_d=0.5, c_e=-0.25, f_e=0.25, incl=-0.42, b_d=1.9 + k,
                                         a_d=2.3 + k, b_e=1.5 - k, a_e=2.0 - k, ap=2.9, bufanda=5, vol=2)
    # agafada: ajupida amb el paraigua clavat a terra per no sortir disparada
    fs["agafada"] = viatgera(ajup=8, c_d=1.35, f_d=2.5, c_e=1.0, f_e=2.4, incl=0.3, b_d=0.75, a_d=0.25,
                             ap=1.1, b_e=0.6, a_e=0.4)
    # asseguda al banc de l'andén (animació inicial): adormida, i desperta
    for i in range(2):
        fs[f"seu_dorm{i}"] = viatgera(c_d=1.35, f_d=1.25, c_e=1.25, f_e=1.2, incl=0.3 + 0.04 * i, b_d=1.0,
                                      a_d=1.7, b_e=0.9, a_e=1.6, ap=0.3, ajup=0.4 * i)
    fs["seu"] = viatgera(c_d=1.35, f_d=1.25, c_e=1.25, f_e=1.2, incl=0.0, b_d=0.8, a_d=1.5, b_e=0.7, a_e=1.4,
                         ap=0.3)
    fs["estira"] = viatgera(mans_amunt=True, paraigua="cap", incl=-0.1, bufanda=1)
    return fs


# ---------------------------------------------------------------------------------------------
# El passatger sense cara
# ---------------------------------------------------------------------------------------------
SW, SH = 52, 62


def sense_cara(c_d=0.0, f_d=0.0, c_e=0.0, f_e=0.0, b_d=0.15, a_d=0.05, b_e=-0.1, a_e=-0.05, incl=0.0,
               ajup=0.0):
    f = Figura(SW, SH, MAT, brillants=("bombi",))
    maluc = (26.0, 40.0 + ajup)
    coll = pt(maluc, math.pi + incl, 17)
    cap = (coll[0] + 1 + incl * 3, coll[1] - 6.5)
    esp = (coll[0], coll[1] + 2.5)
    braç_llarg(f, "vestit_f", (esp[0] - 1, esp[1]), b_e, a_e)
    for mat, dx, a, fl in (("vestit_f", -1.2, c_e, f_e), ("vestit", 1.2, c_d, f_d)):
        m0 = (maluc[0] + dx, maluc[1])
        g = pt(m0, a, 10.5)
        p = pt(g, a - fl, 10.5)
        f.membre(mat, [m0, g, p], [3.0, 2.4, 2.0])
        f.el·lipse("bombi", p[0] - 2.4, p[1] - 2.4, p[0] + 4.2, p[1] + 0.6)
    # americana llarga i estreta
    f.poli("vestit", [(coll[0] - 5, coll[1] + 1), (coll[0] + 4.5, coll[1] + 1), (maluc[0] + 5, maluc[1] + 1),
                      (maluc[0] + 4.5, maluc[1] + 6), (maluc[0] - 5, maluc[1] + 6), (maluc[0] - 5.5, maluc[1])])
    f.poli("camisa", [(coll[0] + 0.5, coll[1] + 1), (coll[0] + 4, coll[1] + 1), (coll[0] + 2.5, coll[1] + 7)])
    f.marca_linia((coll[0] + 2.5, coll[1] + 7), (maluc[0] + 2.5, maluc[1] + 5), -1)
    f.px(coll[0] + 2.5, coll[1] + 3, MAT["bufanda"][1])                                    # la corbata
    f.px(coll[0] + 2.5, coll[1] + 4, MAT["bufanda"][1])
    # el cap: un ou llis sense cara
    f.el·lipse("cara", cap[0] - 5, cap[1] - 6, cap[0] + 5, cap[1] + 6.5, mode="esfera")
    f.marca(cap[0] + 2, cap[1] + 0.5, -1)
    f.marca(cap[0] + 3, cap[1] + 0.5, -1)
    f.poli("bombi", [(cap[0] - 6.5, cap[1] - 3.5), (cap[0] + 7, cap[1] - 3.5), (cap[0] + 7, cap[1] - 2.5),
                     (cap[0] - 6.5, cap[1] - 2.5)])
    f.el·lipse("bombi", cap[0] - 4.5, cap[1] - 10, cap[0] + 4.8, cap[1] - 2.5)
    braç_llarg(f, "vestit", (esp[0] + 1, esp[1] + 0.5), b_d, a_d)
    return f


def braç_llarg(f, mat, esp, a1, a2):
    c = pt(esp, a1, 9.5)
    m = pt(c, a2, 9.5)
    f.membre(mat, [esp, c, m], [2.6, 2.1, 1.8])
    f.membre("cara", [m, pt(m, a2, 3.2)], [1.9, 1.2])                                    # mans llargues
    return m


def fotogrames_sense_cara():
    fs = {"sc_quiet": sense_cara()}
    for i in range(4):
        a, fd, b, fe = cicle_cames(i / 4, 0.4)
        fs[f"sc_camina{i}"] = sense_cara(c_d=a, f_d=fd * 0.6, c_e=b, f_e=fe * 0.6, b_d=-b * 0.5, b_e=-a * 0.5,
                                         incl=0.05)
    fs["sc_prepara"] = sense_cara(c_d=0.2, c_e=-0.3, b_d=2.8, a_d=3.0, b_e=2.5, a_e=2.9, incl=-0.2)
    fs["sc_cop"] = sense_cara(c_d=0.6, f_d=0.3, c_e=-0.5, b_d=1.4, a_d=1.1, b_e=1.2, a_e=0.9, incl=0.4,
                              ajup=1)
    fs["sc_mal"] = sense_cara(c_d=-0.3, c_e=0.3, b_d=-0.8, a_d=-1.2, b_e=-1.0, a_e=-1.3, incl=-0.4)
    fs["sc_atordit"] = sense_cara(c_d=0.1, c_e=-0.1, b_d=0.1, a_d=-0.3, b_e=-0.4, a_e=-0.6, incl=0.3, ajup=2)
    return fs


# ---------------------------------------------------------------------------------------------
# El Revisor (jefe del primer tram): molt alt, abric llarg, gorra de plat, sense cara, farol i perforadora
# ---------------------------------------------------------------------------------------------
RW, RH = 96, 104
R_BASE = {"c_d": 0.0, "f_d": 0.0, "c_e": 0.0, "f_e": 0.0, "b_d": 0.35, "a_d": 0.2, "b_e": -0.6, "a_e": -0.1,
          "incl": 0.0, "ajup": 0.0, "ap": None, "ulls": 1.0, "agenoll": False, "farol": True}


def perforadora(f, ma, a):
    """La perforadora de bitllets gegant: el mànec a la mà i el cap de llautó en la direcció a."""
    ux, uy = math.sin(a), math.cos(a)
    nx, ny = -uy, ux
    cap = (ma[0] + ux * 9, ma[1] + uy * 9)
    f.membre("uniforme_f", [ma, cap], 1.6, mode="pla")
    pts = [(cap[0] + nx * 5 - ux * 2, cap[1] + ny * 5 - uy * 2), (cap[0] + nx * 5 + ux * 7, cap[1] + ny * 5 + uy * 7),
           (cap[0] - nx * 4 + ux * 8, cap[1] - ny * 4 + uy * 8), (cap[0] - nx * 5 - ux * 1, cap[1] - ny * 5 - uy * 1)]
    f.poli("llauto", pts)
    f.marca_linia((cap[0] + ux * 3 + nx * 4, cap[1] + uy * 3 + ny * 4),
                  (cap[0] + ux * 3 - nx * 4, cap[1] + uy * 3 - ny * 4), -1)
    f.cercle("ombra", cap[0] + ux * 5, cap[1] + uy * 5, 1.2, mode="pla")
    return (cap[0] + ux * 8, cap[1] + uy * 8)


def farol(f, ma):
    x, y = ma[0], ma[1] + 2
    f.membre("llauto", [(x, y - 2), (x, y + 1)], 0.6, mode="pla")
    f.poli("llauto", [(x - 4, y + 1), (x + 4, y + 1), (x + 3, y + 3), (x - 3, y + 3)])
    f.rect("farol", x - 3, y + 3, x + 3, y + 10, mode="brilla")
    f.rect("llauto", x - 4, y + 10, x + 4, y + 12)
    f.membre("llauto", [(x, y + 3), (x, y + 10)], 0.4, mode="pla")


def braç_rev(f, mat, esp, a1, a2):
    c = pt(esp, a1, 13)
    m = pt(c, a2, 12)
    f.membre(mat, [esp, c, m], [3.2, 2.8, 2.4])
    f.membre("llauto", [pt(c, a2, 9.5), pt(c, a2, 10.5)], 2.7, mode="pla")              # el puny daurat
    f.el·lipse("guant", m[0] - 2.4, m[1] - 2.2, m[0] + 2.4, m[1] + 2.6)
    return m


def revisor(**pose):
    p = dict(R_BASE, **pose)
    f = Figura(RW, RH, MAT, brillants=("llauto", "farol", "ull"))
    x0 = RW // 2
    alt_cama = 15.5
    maluc = (x0, RH - 1 - 2 * alt_cama + 1 + p["ajup"])
    inc = p["incl"]
    coll = pt(maluc, math.pi + inc, 30 - p["ajup"] * 0.2)
    esp = (coll[0], coll[1] + 3)
    cap = (coll[0] + 1.5 + inc * 4, coll[1] - 7.5)
    # braç del farol (darrere)
    m_e = braç_rev(f, "uniforme_f", (esp[0] - 2, esp[1]), p["b_e"], p["a_e"])
    if p["farol"]:
        farol(f, m_e)
    # cames
    if p["agenoll"]:
        cames = (("uniforme_f", -1.5, 1.45, 1.5), ("uniforme", 1.5, 0.2, 2.0))
    else:
        cames = (("uniforme_f", -1.5, p["c_e"], p["f_e"]), ("uniforme", 1.5, p["c_d"], p["f_d"]))
    for mat, dx, a, fl in cames:
        m0 = (maluc[0] + dx, maluc[1])
        g = pt(m0, a, alt_cama)
        q = pt(g, a - fl, alt_cama)
        f.membre(mat, [m0, g, q], [3.4, 2.8, 2.4])
        f.el·lipse("ombra", q[0] - 3, q[1] - 2.8, q[0] + 5, q[1] + 0.6)
    # l'abric llarg: del coll fins a mitja canyella
    baix = min(RH - 9, maluc[1] + 22 - p["ajup"] * 0.5)
    abric = [(coll[0] - 6, coll[1] + 1), (coll[0] + 5.5, coll[1] + 1), (maluc[0] + 6.5, maluc[1] - 2),
             (maluc[0] + 9 + inc * 6, baix), (maluc[0] - 8 + inc * 6, baix + 0.5), (maluc[0] - 7, maluc[1] - 2)]
    f.poli("uniforme", abric)
    f.marca_linia((coll[0] + 2, coll[1] + 2), (maluc[0] + 2.5 + inc * 3, baix - 1), -1)
    for k in range(5):                                                                      # botons de llautó
        t = 0.12 + k * 0.17
        bx = coll[0] + 3.6 + (maluc[0] - coll[0]) * t
        by = coll[1] + 3 + (maluc[1] - coll[1]) * t
        f.px(bx, by, MAT["llauto"][3])
    f.rect("ombra", maluc[0] - 6.5, maluc[1] - 4, maluc[0] + 6.5, maluc[1] - 2.5, mode="pla")  # cinturó
    f.px(maluc[0] + 3, maluc[1] - 3.2, MAT["llauto"][3])
    f.poli("uniforme_f", [(coll[0] - 4, coll[1] - 0.5), (coll[0] + 5, coll[1] - 0.5), (coll[0] + 4, coll[1] + 3),
                          (coll[0] - 3, coll[1] + 3)])                                       # coll alt
    # el cap: només ombra sota la visera i dos punts de llum
    f.el·lipse("ombra", cap[0] - 4.2, cap[1] - 5, cap[0] + 4.6, cap[1] + 5.5)
    if p["ulls"] > 0:
        col = MAT["ull"][4 if p["ulls"] > 1 else 2]
        f.px(cap[0] + 1.8, cap[1] - 0.2, col)
        f.px(cap[0] + 4.0, cap[1] - 0.2, col)
    # gorra de plat
    f.poli("uniforme", [(cap[0] - 6, cap[1] - 5), (cap[0] - 4.5, cap[1] - 9.5), (cap[0] + 5.5, cap[1] - 10),
                        (cap[0] + 7, cap[1] - 5)])
    f.rect("ombra", cap[0] - 5.5, cap[1] - 5.5, cap[0] + 6.5, cap[1] - 4, mode="pla")
    f.poli("ombra", [(cap[0] + 3, cap[1] - 4.5), (cap[0] + 10, cap[1] - 4), (cap[0] + 9, cap[1] - 2.8),
                     (cap[0] + 3, cap[1] - 3.4)])                                            # visera
    f.el·lipse("llauto", cap[0] + 1, cap[1] - 8.6, cap[0] + 4, cap[1] - 6)
    # braç de la perforadora (davant)
    m_d = braç_rev(f, "uniforme", (esp[0] + 1.5, esp[1] + 0.5), p["b_d"], p["a_d"])
    if p["ap"] is not None:
        perforadora(f, m_d, p["ap"])
    return f


def fotogrames_revisor():
    fs = {}
    fs["rv_quiet0"] = revisor(ap=1.2)
    fs["rv_quiet1"] = revisor(ap=1.25, ajup=0.8, b_d=0.4, a_d=0.25)
    for i in range(4):
        a, fd, b, fe = cicle_cames(i / 4, 0.42)
        fs[f"rv_camina{i}"] = revisor(c_d=a, f_d=fd * 0.7, c_e=b, f_e=fe * 0.7, incl=0.12, b_d=0.3 - b * 0.4,
                                      a_d=0.15 - b * 0.4, b_e=-0.6 - a * 0.3, ap=1.2, ajup=abs(math.sin(i * math.pi / 2)) * -0.8)
    # alça la perforadora per sobre del cap
    fs["rv_alça"] = revisor(c_d=0.25, f_d=0.2, c_e=-0.25, f_e=0.2, incl=-0.15, b_d=3.0, a_d=3.2, ap=3.4, ulls=2)
    # cop: s'inclina i clava la perforadora a terra davant seu
    fs["rv_cop"] = revisor(c_d=0.55, f_d=0.45, c_e=-0.4, f_e=0.3, incl=0.75, b_d=1.0, a_d=0.25, ap=0.2, ajup=4,
                           ulls=2, b_e=-0.6, a_e=-0.4)
    # encallat: la perforadora clavada, estira per treure-la
    for i in range(2):
        fs[f"rv_encallat{i}"] = revisor(c_d=0.55, f_d=0.45, c_e=-0.45, f_e=0.3, incl=0.7 - 0.08 * i, b_d=0.95 - 0.06 * i,
                                        a_d=0.3, ap=0.25, ajup=4, ulls=1, b_e=-0.5, a_e=-0.3)
    # «Billete, por favor»: estira el braç per agafar-te
    for i in range(2):
        a, fd, b, fe = cicle_cames(i / 2, 0.6)
        fs[f"rv_estira{i}"] = revisor(c_d=a, f_d=fd * 0.6, c_e=b, f_e=fe * 0.6, incl=0.35, b_d=1.6, a_d=1.55,
                                      ap=None, b_e=-0.6, a_e=-0.5, ulls=2)
    for i in range(2):
        fs[f"rv_atordit{i}"] = revisor(c_d=0.1, c_e=-0.15, incl=0.45 + 0.05 * i, b_d=0.05, a_d=-0.15, ap=0.1,
                                       ajup=3 + i, b_e=-0.1, a_e=0.0, ulls=0 if i else 1)
    fs["rv_mal"] = revisor(c_d=-0.3, c_e=0.3, incl=-0.35, b_d=-0.8, a_d=-1.1, ap=-0.5, b_e=-1.0, a_e=-1.2, ulls=2)
    fs["rv_vençut"] = revisor(agenoll=True, incl=0.55, ajup=12, b_d=0.2, a_d=0.1, ap=None, b_e=0.1, a_e=0.0,
                              farol=False, ulls=0)
    return fs


# ---------------------------------------------------------------------------------------------
# La maleta (de decorat, i la viva)
# ---------------------------------------------------------------------------------------------
MW, MH = 30, 26


def maleta(obertura=0.0, alt=1.0, ulls=False, mat="cuir"):
    f = Figura(MW, MH, MAT, brillants=("sivella",))
    base = MH - 1
    h = 13 * alt
    x0, x1 = 3, 27
    top = base - h
    if obertura > 0:                                  # la tapa s'aixeca i deixa veure la boca
        ang = obertura * 0.7
        f.poli("boca", [(x0 + 1, top + 3), (x1 - 1, top + 3), (x1 - 1, top + 6), (x0 + 1, top + 6)])
        f.poli(mat, [(x0, top + 4), (x1, top + 4), (x1, base), (x0, base)])
        for i in range(6):
            dx = x0 + 3 + i * 3.6
            f.poli("dent", [(dx, top + 4), (dx + 2.4, top + 4), (dx + 1.2, top + 1.2)], mode="pla")
        piv = (x0, top + 4)
        tapa = [(x0, top + 4), (x1, top + 4), (x1, top), (x0 + 1, top - 1)]
        tapa = [(piv[0] + (x - piv[0]) * math.cos(-ang) - (y - piv[1]) * math.sin(-ang),
                 piv[1] + (x - piv[0]) * math.sin(-ang) + (y - piv[1]) * math.cos(-ang)) for x, y in tapa]
        f.poli(mat, tapa)
        for i in range(5):
            t = (i + 0.5) / 5
            bx = tapa[0][0] + (tapa[1][0] - tapa[0][0]) * t
            by = tapa[0][1] + (tapa[1][1] - tapa[0][1]) * t
            f.poli("dent", [(bx - 1.2, by), (bx + 1.2, by), (bx, by + 2.6)], mode="pla")
    else:
        f.poli(mat, [(x0, top + 1), (x0 + 1, top), (x1 - 1, top), (x1, top + 1), (x1, base), (x0, base)])
        f.marca_linia((x0 + 1, top + 4), (x1 - 1, top + 4), -1)
        if ulls:
            f.px(x0 + 8, top + 4, MAT["ull"][2])
            f.px(x0 + 15, top + 4, MAT["ull"][2])
    # corretges i sivelles
    for sx in (x0 + 6, x1 - 7):
        f.marca_linia((sx, top + 1), (sx, base - 1), -1)
        f.rect("sivella", sx - 1, top + 5, sx + 1, top + 7, mode="pla")
    f.membre("cuir_f", [(13, top - 0.5), (13, top - 3), (17, top - 3), (17, top - 0.5)], 0.9, mode="pla")
    return f


def fotogrames_maleta():
    return {"maleta": maleta(), "maleta_ulls": maleta(ulls=True), "maleta_obre": maleta(obertura=1.0),
            "maleta_salt": maleta(obertura=0.6, alt=1.15)}


# ---------------------------------------------------------------------------------------------
# El polissó
# ---------------------------------------------------------------------------------------------
PW, PH = 40, 40


def polisso(t=None, fuig=False):
    f = Figura(PW, PH, MAT, brillants=("ull",))
    if t is None:
        a, fd, b, fe = 0.2, 0.9, -0.1, 0.8
    else:
        a, fd, b, fe = cicle_cames(t, 0.85)
    maluc = (20.0, 30.0)
    for mat, dx, aa, fl in (("drap_f", -1, b, fe), ("drap", 1, a, fd)):
        m0 = (maluc[0] + dx, maluc[1])
        g = pt(m0, aa, 4.6)
        p = pt(g, aa - fl, 4.6)
        f.membre(mat, [m0, g, p], [2.2, 1.9, 1.6])
        f.el·lipse("bota", p[0] - 1.8, p[1] - 2, p[0] + 2.8, p[1] + 0.6)
    # el sac a l'esquena
    f.el·lipse("sac", 7, 13, 19, 26)
    f.membre("sac", [(16, 14), (13, 10)], [1.6, 1.0])
    if fuig:
        f.px(12, 18, MAT["ull"][3])
        f.px(14, 21, MAT["ull"][2])
    # cos encorbat amb caputxa
    f.poli("drap", [(15, 15), (24, 13), (29, 18), (27, 28), (24, 32), (15, 32), (13, 24)])
    f.poli("drap", [(19, 7), (25, 5), (31, 8), (33, 14), (31, 19), (25, 20), (20, 17), (18, 12)])
    f.el·lipse("drap_f", 25, 9, 32, 17, mode="fosc")
    f.px(28, 12, MAT["ull"][4])
    f.px(30, 12, MAT["ull"][4])
    f.px(28, 13, MAT["ull"][2])
    f.px(30, 13, MAT["ull"][2])
    f.membre("drap", [(25, 20), pt((25, 20), 1.2 + (0.4 if t is None else math.sin(t * math.tau) * 0.6), 5),
                      pt(pt((25, 20), 1.2, 5), 1.6, 4)], [1.8, 1.5, 1.3])
    return f


def fotogrames_polisso():
    fs = {"po_quiet": polisso()}
    for i in range(4):
        fs[f"po_corre{i}"] = polisso(i / 4)
        fs[f"po_fuig{i}"] = polisso(i / 4, fuig=True)
    return fs


# ---------------------------------------------------------------------------------------------
def main():
    imatges, ancores = {}, {}
    grups = [(fotogrames_viatgera(), VW), (fotogrames_sense_cara(), SW), (fotogrames_maleta(), MW),
             (fotogrames_polisso(), PW), (fotogrames_revisor(), RW)]
    for fs, w in grups:
        for nom, fig in fs.items():
            s = fig.superficie(fins_a_baix=True)
            im, (ox, oy) = retallar(s)
            imatges[nom] = im
            ancores[nom] = (w // 2 - ox, s.get_height() - oy)
    # el passatger adormit (estirat a la llitera): el quiet girat 90°
    adorm = pygame.transform.rotate(imatges["sc_quiet"], 90)
    imatges["sc_dorm"] = adorm
    ancores["sc_dorm"] = (adorm.get_width() // 2, adorm.get_height())
    atles, rects = empaquetar(imatges, ample=512)
    os.makedirs(SORTIDA, exist_ok=True)
    pygame.image.save(atles, os.path.join(SORTIDA, "personatges.png"))
    dades = {n: {"r": rects[n], "a": list(ancores[n])} for n in rects}
    with open(os.path.join(SORTIDA, "personatges.json"), "w", encoding="utf-8") as fh:
        json.dump(dades, fh, separators=(",", ":"), sort_keys=True)
    print(f"personatges: {len(rects)} fotogrames, atles {atles.get_size()}")
    if len(sys.argv) > 1:
        vista(imatges, sys.argv[1])


def vista(imatges, ruta, escala=4):
    noms = list(imatges)
    col = 10
    cel = 64
    files = (len(noms) + col - 1) // col
    s = pygame.Surface((col * cel, files * cel))
    s.fill((60, 46, 40))
    for i, n in enumerate(noms):
        im = imatges[n]
        x, y = (i % col) * cel, (i // col) * cel
        s.blit(im, (x + (cel - im.get_width()) // 2, y + cel - im.get_height() - 2))
    pygame.image.save(pygame.transform.scale_by(s, escala), ruta)


if __name__ == "__main__":
    main()
