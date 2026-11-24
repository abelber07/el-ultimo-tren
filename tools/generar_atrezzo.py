"""Genera el mobiliari i els objectes dels vagons a assets/img/atrezzo.png + atrezzo.json.

    python tools/generar_atrezzo.py [vista.png]

Seients de vellut, taules, llums de paret, cortines, portes, llitera, taules del restaurant, sacs de correu,
caixes, bagul, la màquina expenedora, i els objectes petits (pa, bitllet, ampolla) i les icones del HUD.
L'àncora de cada peça és el mig de la base (on toca a terra).
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
    "vellut": [(48, 8, 16), (120, 20, 34), (166, 36, 48), (204, 64, 70), (236, 116, 116)],
    "fusta": [(30, 14, 10), (74, 38, 22), (104, 58, 32), (138, 84, 48), (176, 120, 74)],
    "fusta_c": [(44, 24, 14), (110, 66, 34), (150, 98, 52), (188, 134, 78), (224, 178, 118)],
    "llauto": [(62, 40, 14), (140, 100, 36), (196, 150, 58), (232, 196, 100), (255, 238, 176)],
    "vidre": [(110, 54, 10), (220, 130, 30), (255, 186, 70), (255, 222, 140), (255, 248, 214)],
    "tela": [(80, 70, 66), (176, 168, 156), (214, 206, 192), (236, 230, 218), (252, 250, 242)],
    "manta": [(22, 34, 52), (46, 70, 104), (66, 96, 136), (96, 128, 168), (140, 170, 204)],
    "coixi": [(90, 86, 96), (180, 176, 186), (214, 212, 220), (234, 232, 238), (250, 250, 254)],
    "sac": [(56, 44, 28), (126, 102, 64), (166, 138, 90), (200, 176, 124), (232, 214, 168)],
    "caixa": [(40, 28, 18), (96, 70, 42), (130, 98, 58), (162, 128, 80), (198, 166, 112)],
    "ferro": [(16, 16, 22), (44, 46, 58), (66, 70, 86), (94, 100, 118), (136, 142, 162)],
    "cuir": [(40, 20, 12), (104, 54, 28), (146, 82, 42), (184, 116, 62), (222, 160, 100)],
    "verd": [(10, 30, 26), (24, 70, 56), (40, 104, 80), (70, 140, 104), (120, 184, 140)],
    "pa": [(70, 36, 12), (150, 88, 34), (198, 132, 58), (230, 176, 96), (252, 222, 156)],
    "paper": [(90, 80, 60), (184, 170, 136), (222, 210, 176), (240, 232, 206), (255, 252, 236)],
    "or": [(80, 50, 6), (178, 124, 20), (230, 176, 40), (255, 214, 90), (255, 244, 180)],
    "cor": [(60, 6, 12), (150, 20, 32), (210, 44, 54), (246, 92, 92), (255, 170, 160)],
    "buit": [(20, 16, 22), (44, 38, 48), (62, 56, 68), (84, 78, 90), (112, 106, 118)],
    "ampolla": [(10, 34, 22), (24, 80, 48), (40, 120, 70), (80, 170, 110), (170, 230, 190)],
    "vermell": [(60, 10, 10), (160, 30, 30), (220, 60, 50), (255, 120, 90), (255, 200, 170)],
    "llum_v": [(10, 50, 20), (30, 140, 60), (70, 210, 100), (150, 250, 160), (230, 255, 230)],
}
comprovar_paleta(MAT)
PECES = {}


def peça(nom, w, h, brillants=()):
    def dec(fn):
        PECES[nom] = (w, h, brillants, fn)
        return fn
    return dec


@peça("seient", 30, 40, ("llauto",))
def seient(f):
    """Seient de vellut mirant a la dreta: el respatller a l'esquerra."""
    f.rect("fusta", 3, 30, 27, 33)
    f.membre("ferro", [(6, 33), (6, 39)], 1.2)
    f.membre("ferro", [(24, 33), (24, 39)], 1.2)
    f.poli("vellut", [(2, 3), (8, 1), (10, 4), (10, 30), (2, 30)])
    f.poli("vellut", [(8, 22), (26, 21), (28, 24), (27, 30), (8, 30)])
    for y in (8, 14, 20):
        f.marca_linia((4, y), (8, y), -1)
    f.marca_linia((12, 25), (26, 25), 1)
    f.membre("llauto", [(9, 18), (16, 18), (16, 22)], 0.9, mode="pla")


@peça("tauleta", 18, 26, ())
def tauleta(f):
    f.rect("fusta_c", 1, 2, 17, 5)
    f.membre("fusta", [(9, 5), (9, 25)], 1.4)
    f.rect("fusta", 5, 23, 13, 25)


@peça("llum", 12, 18, ("llauto", "vidre"))
def llum(f):
    f.rect("llauto", 4, 0, 8, 2, mode="pla")
    f.poli("vidre", [(3, 4), (9, 4), (10, 11), (6, 13), (2, 11)], mode="brilla")
    f.poli("llauto", [(2, 3), (10, 3), (9, 5), (3, 5)])
    f.poli("llauto", [(3, 12), (9, 12), (7, 15), (5, 15)])
    f.membre("llauto", [(6, 15), (6, 17)], 0.8)


@peça("llum_penjant", 16, 24, ("llauto", "vidre"))
def llum_penjant(f):
    f.membre("llauto", [(8, 0), (8, 10)], 0.6, mode="pla")
    f.poli("llauto", [(2, 16), (8, 9), (14, 16)])
    f.poli("vidre", [(4, 16), (12, 16), (10, 21), (6, 21)], mode="brilla")


@peça("cortina", 12, 66, ())
def cortina(f):
    f.rect("llauto", 0, 0, 12, 2, mode="pla")
    f.poli("vellut", [(1, 2), (11, 2), (10, 30), (12, 64), (2, 64), (4, 32)])
    for x in (4, 7, 10):
        f.marca_linia((x, 4), (x - 1, 28), -1)
        f.marca_linia((x - 1, 36), (x, 62), -1)
    f.membre("llauto", [(2, 32), (10, 32)], 1.0, mode="pla")


@peça("porta", 26, 70, ("llauto",))
def porta(f):
    f.rect("fusta", 1, 1, 25, 69)
    f.rect("fusta_c", 4, 36, 22, 64, mode="pla")
    f.rect("ferro", 6, 8, 20, 28, mode="fosc")
    f.marca_linia((13, 8), (13, 28), 1)
    f.marca_linia((6, 18), (20, 18), 1)
    f.cercle("llauto", 20, 40, 1.6)


@peça("llitera", 76, 16, ("llauto",))
def llitera(f):
    f.rect("fusta", 0, 10, 76, 15)
    f.rect("manta", 6, 4, 70, 10)
    f.el·lipse("coixi", 2, 3, 16, 10)
    for x in (22, 36, 50, 62):
        f.marca_linia((x, 5), (x + 2, 9), -1)
    f.membre("llauto", [(1, 10), (1, 2)], 1.0)
    f.membre("llauto", [(75, 10), (75, 2)], 1.0)


@peça("taula", 46, 30, ("llauto", "vidre"))
def taula(f):
    f.poli("tela", [(0, 10), (46, 10), (45, 19), (40, 21), (6, 21), (1, 19)])
    f.membre("fusta", [(23, 21), (23, 29)], 2.0)
    f.rect("fusta", 15, 27, 31, 29)
    f.poli("vidre", [(20, 4), (26, 4), (27, 9), (19, 9)], mode="brilla")       # llumeta de taula
    f.rect("llauto", 18, 8, 28, 10)
    f.el·lipse("tela", 32, 7, 40, 10)                                         # plat


@peça("cadira", 16, 30, ())
def cadira(f):
    f.poli("fusta", [(1, 0), (4, 0), (4, 18), (15, 18), (15, 21), (1, 21)])
    f.rect("vellut", 4, 15, 15, 18)
    f.membre("fusta", [(2, 21), (2, 29)], 1.0)
    f.membre("fusta", [(14, 21), (14, 29)], 1.0)


@peça("saca", 20, 22, ())
def saca(f):
    f.poli("sac", [(3, 21), (1, 12), (4, 5), (8, 3), (12, 3), (16, 6), (19, 13), (17, 21)])
    f.membre("sac", [(8, 3), (10, 0), (12, 3)], 1.1)
    f.marca_linia((6, 8), (14, 8), -1)
    f.rect("vermell", 8, 12, 13, 15, mode="pla")


@peça("caixa", 26, 24, ())
def caixa(f):
    f.rect("caixa", 0, 0, 26, 24)
    for y in (7, 15):
        f.marca_linia((1, y), (25, y), -1)
    f.marca_linia((1, 1), (25, 23), -1)
    f.rect("ferro", 0, 0, 3, 24, mode="pla")
    f.rect("ferro", 23, 0, 26, 24, mode="pla")


@peça("bagul", 32, 24, ("llauto",))
def bagul(f):
    f.rect("verd", 1, 9, 31, 23)
    f.poli("verd", [(1, 9), (3, 3), (16, 1), (29, 3), (31, 9)])
    for x in (6, 26):
        f.rect("llauto", x - 1, 2, x + 1, 23, mode="pla")
    f.rect("llauto", 14, 8, 18, 13)


@peça("bagul_obert", 32, 30, ("llauto", "or"))
def bagul_obert(f):
    f.poli("verd", [(2, 15), (4, 1), (28, 1), (30, 15)], mode="fosc")
    f.rect("verd", 1, 15, 31, 29)
    f.el·lipse("or", 6, 11, 26, 18)
    for x in (6, 26):
        f.rect("llauto", x - 1, 15, x + 1, 29, mode="pla")


@peça("maquina", 38, 66, ("llauto", "vidre"))
def maquina(f):
    """La màquina expenedora antiga: caixa de fusta amb aparador de vidre i rètol lluminós."""
    f.rect("fusta", 2, 6, 36, 65)
    f.poli("llauto", [(0, 6), (19, 0), (38, 6)])
    f.rect("vidre", 6, 9, 32, 15, mode="brilla")
    f.rect("ferro", 6, 19, 32, 46, mode="fosc")
    for y in (27, 36):
        f.marca_linia((7, y), (31, y), 2)
    f.rect("llauto", 13, 50, 25, 55)
    f.rect("ferro", 10, 58, 28, 62, mode="fosc")
    f.cercle("llauto", 30, 52, 1.8)


@peça("escotilla", 28, 6, ())
def escotilla(f):
    f.rect("ferro", 0, 1, 28, 5)
    f.marca_linia((2, 3), (26, 3), 1)
    f.cercle("ferro", 14, 1.5, 1.6)


@peça("pa", 14, 9, ())
def pa(f):
    f.el·lipse("pa", 0, 1, 14, 9)
    for x in (4, 7, 10):
        f.marca_linia((x, 2), (x - 1, 5), -1)


@peça("bitllet", 12, 8, ())
def bitllet(f):
    f.rect("paper", 0, 0, 12, 8)
    f.rect("vermell", 0, 0, 3, 8, mode="pla")
    f.marca_linia((5, 3), (10, 3), -1)
    f.marca_linia((5, 5), (9, 5), -1)


@peça("ampolla", 8, 16, ())
def ampolla(f):
    f.poli("ampolla", [(2, 15), (1, 8), (3, 5), (3, 1), (5, 1), (5, 5), (7, 8), (6, 15)])
    f.rect("paper", 2, 9, 6, 12, mode="pla")


@peça("cor", 11, 10, ())
def cor(f):
    f.poli("cor", [(5.5, 9.5), (0.5, 4), (0.5, 2), (2.5, 0.5), (5.5, 2), (8.5, 0.5), (10.5, 2), (10.5, 4)])


@peça("cor_buit", 11, 10, ())
def cor_buit(f):
    f.poli("buit", [(5.5, 9.5), (0.5, 4), (0.5, 2), (2.5, 0.5), (5.5, 2), (8.5, 0.5), (10.5, 2), (10.5, 4)])


@peça("cor_llauna", 13, 12, ())
def cor_llauna(f):
    f.poli("ferro", [(6.5, 11.5), (0.5, 5), (0.5, 2.5), (3, 0.5), (6.5, 2.5), (10, 0.5), (12.5, 2.5),
                     (12.5, 5)])
    f.cercle("cor", 6.5, 5.5, 1.8)


@peça("rellotge", 14, 16, ("llauto", "paper"))
def rellotge(f):
    f.cercle("llauto", 7, 2, 1.4)
    f.cercle("llauto", 7, 9, 6.5)
    f.cercle("paper", 7, 9, 5, mode="pla")
    f.linia((7, 9), (7, 5), MAT["ferro"][0])
    f.linia((7, 9), (10, 9), MAT["ferro"][0])


@peça("llum_porta_v", 6, 6, ("vermell",))
def llum_porta_v(f):
    f.cercle("vermell", 3, 3, 2.6, mode="brilla")


@peça("llum_porta_g", 6, 6, ("llum_v",))
def llum_porta_g(f):
    f.cercle("llum_v", 3, 3, 2.6, mode="brilla")


def main():
    imatges, ancores = {}, {}
    for nom, (w, h, br, fn) in PECES.items():
        f = Figura(w, h, MAT, brillants=br)
        fn(f)
        s = f.superficie(fins_a_baix=True)
        im, (ox, oy) = retallar(s)
        imatges[nom] = im
        ancores[nom] = (w // 2 - ox, h - oy)
    atles, rects = empaquetar(imatges, ample=512)
    pygame.image.save(atles, os.path.join(SORTIDA, "atrezzo.png"))
    with open(os.path.join(SORTIDA, "atrezzo.json"), "w", encoding="utf-8") as fh:
        json.dump({n: {"r": rects[n], "a": list(ancores[n])} for n in rects}, fh, separators=(",", ":"),
                  sort_keys=True)
    print(f"atrezzo: {len(rects)} peces, atles {atles.get_size()}")
    if len(sys.argv) > 1:
        col, cel = 8, 80
        noms = list(imatges)
        v = pygame.Surface((col * cel, ((len(noms) + col - 1) // col) * cel))
        v.fill((60, 40, 30))
        for i, n in enumerate(noms):
            im = imatges[n]
            v.blit(im, ((i % col) * cel + (cel - im.get_width()) // 2, (i // col) * cel + cel - im.get_height() - 4))
        pygame.image.save(pygame.transform.scale_by(v, 3), sys.argv[1])


if __name__ == "__main__":
    main()
