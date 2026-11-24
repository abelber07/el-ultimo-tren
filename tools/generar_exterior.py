"""Genera el tren vist de fora (menú i animació inicial) a assets/img/exterior.png + exterior.json.

    python tools/generar_exterior.py [vista.png]

La locomotora de vapor i el ténder (sense rodes: el joc les pinta girant amb les bieles), el banc i la farola de
l'andén i el rellotge de l'estació. L'àncora és el mig de baix (on toca el carril o el terra).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pygame  # noqa: E402
from pintor import Figura, comprovar_paleta, empaquetar, retallar  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
SORTIDA = os.path.join(AQUI, "..", "assets", "img")

MAT = {
    "ferro": [(10, 12, 20), (30, 34, 50), (46, 52, 72), (70, 78, 102), (112, 122, 150)],
    "ferro_f": [(8, 8, 14), (20, 22, 34), (32, 36, 50), (48, 54, 72), (74, 80, 102)],
    "llauto": [(62, 40, 14), (140, 100, 36), (196, 150, 58), (232, 196, 100), (255, 238, 176)],
    "vermell": [(50, 10, 12), (120, 26, 30), (168, 44, 44), (206, 78, 70), (240, 130, 116)],
    "vidre": [(110, 54, 10), (220, 130, 30), (255, 186, 70), (255, 222, 140), (255, 248, 214)],
    "carbo": [(4, 4, 6), (14, 14, 18), (24, 24, 30), (40, 40, 48), (70, 70, 82)],
    "fusta": [(30, 16, 10), (76, 42, 24), (106, 62, 34), (140, 88, 50), (180, 126, 78)],
    "pedra": [(20, 20, 28), (48, 48, 60), (68, 68, 82), (92, 92, 108), (126, 126, 144)],
    "paper": [(90, 80, 60), (184, 170, 136), (222, 210, 176), (240, 232, 206), (255, 252, 236)],
    "granat": [(30, 8, 12), (72, 18, 24), (100, 28, 32), (130, 44, 44), (168, 74, 68)],
    "granat_f": [(22, 6, 10), (52, 14, 20), (74, 22, 26), (98, 34, 36), (128, 56, 54)],
    "mao": [(30, 14, 14), (70, 34, 30), (96, 48, 40), (122, 66, 54), (156, 96, 78)],
    "teula": [(12, 14, 24), (28, 32, 48), (42, 48, 68), (60, 68, 92), (90, 100, 130)],
    "llum_v": [(70, 10, 10), (170, 30, 24), (230, 60, 40), (255, 120, 90), (255, 200, 180)],
}
comprovar_paleta(MAT)

# on van les rodes (respecte de l'àncora: x des del mig, y des del carril) i el radi
RODES_LOCO = [(-55, -12, 10), (-20, -14, 14), (12, -14, 14), (44, -14, 14), (72, -8, 7)]
RODES_TENDER = [(-20, -9, 9), (20, -9, 9)]


def locomotora(f):
    """Mirant a la dreta. Llenç 190x96; el carril a y=96."""
    # bastidor i passarel·la
    f.rect("ferro_f", 14, 70, 176, 76)
    f.rect("vermell", 10, 66, 178, 70, mode="pla")
    # cabina
    f.rect("ferro", 14, 18, 60, 66)
    f.poli("ferro_f", [(8, 18), (12, 12), (62, 12), (66, 18)])
    f.rect("vidre", 22, 26, 36, 42, mode="brilla")
    f.rect("vidre", 42, 26, 54, 42, mode="brilla")
    f.marca_linia((14, 50), (60, 50), -1)
    f.rect("llauto", 14, 46, 60, 48, mode="pla")
    # caldera
    f.rect("ferro", 60, 34, 156, 66)
    f.el·lipse("ferro", 150, 33, 170, 66)
    f.marca_linia((60, 38), (156, 38), 1)
    for x in (82, 108, 134):
        f.rect("llauto", x, 34, x + 2, 66, mode="pla")
    f.el·lipse("ferro_f", 156, 36, 172, 64, mode="fosc")            # la caixa de fums
    # xemeneia, dom i sorrera
    f.poli("ferro", [(146, 34), (148, 12), (160, 12), (162, 34)])
    f.poli("ferro_f", [(142, 12), (144, 4), (164, 4), (166, 12)])
    f.el·lipse("llauto", 110, 22, 128, 36)
    f.rect("llauto", 112, 30, 126, 35)
    f.el·lipse("ferro", 84, 26, 98, 37)
    f.membre("llauto", [(70, 34), (70, 26)], 1.2)                   # xiulet
    # far
    f.rect("llauto", 166, 26, 180, 36)
    f.rect("vidre", 176, 27, 181, 35, mode="brilla")
    # cilindre i llevaneu
    f.rect("ferro_f", 140, 70, 166, 84)
    f.marca_linia((142, 77), (164, 77), 1)
    f.poli("vermell", [(166, 76), (178, 76), (190, 95), (160, 95)])
    for x in (168, 174, 180):
        f.marca_linia((x, 78), (x + 4, 94), -1)
    # barana
    f.membre("llauto", [(62, 32), (150, 32)], 0.6, mode="pla")


def tender(f):
    """Llenç 80x80; el carril a y=80."""
    f.rect("ferro", 4, 30, 76, 68)
    f.rect("llauto", 4, 30, 76, 33, mode="pla")
    f.marca_linia((8, 50), (72, 50), -1)
    f.poli("carbo", [(8, 30), (16, 20), (28, 16), (44, 18), (58, 14), (70, 22), (74, 30)])
    for x, y in ((20, 22), (34, 19), (50, 20), (62, 21)):
        f.marca(x, y, 2)
    f.rect("ferro_f", 6, 68, 74, 72)


def banc(f):
    """Banc de l'andén: 64x30."""
    f.rect("fusta", 2, 14, 62, 18)
    for y in (2, 7):
        f.rect("fusta", 4, y, 60, y + 4)
    f.membre("ferro", [(8, 2), (8, 29)], 1.4)
    f.membre("ferro", [(56, 2), (56, 29)], 1.4)
    f.membre("ferro", [(8, 18), (14, 29)], 1.0)
    f.membre("ferro", [(56, 18), (50, 29)], 1.0)


def farola(f):
    """Farola de gas: 26x120."""
    f.rect("ferro", 10, 110, 16, 119)
    f.membre("ferro", [(13, 112), (13, 22)], 2.0)
    f.membre("ferro", [(13, 60), (13, 54)], 3.0)
    f.poli("ferro", [(5, 12), (13, 6), (21, 12)])
    f.rect("vidre", 7, 12, 19, 24, mode="brilla")
    f.poli("ferro", [(6, 24), (20, 24), (17, 28), (9, 28)])
    f.membre("ferro", [(13, 6), (13, 1)], 1.0)


def rellotge(f):
    """El rellotge de l'estació: 28x34."""
    f.membre("ferro", [(14, 0), (14, 6)], 1.2)
    f.cercle("llauto", 14, 19, 13)
    f.cercle("paper", 14, 19, 10, mode="pla")
    for k in range(12):
        import math
        a = k * math.tau / 12
        f.px(14 + math.cos(a) * 8, 19 + math.sin(a) * 8, MAT["ferro"][1])
    f.linia((14, 19), (14, 12), MAT["ferro"][0])
    f.linia((14, 19), (19, 21), MAT["ferro"][0])


def _cos_vago(f, w):
    f.rect("ferro_f", 6, 62, w - 6, 68)
    f.rect("granat", 4, 14, w - 4, 62)
    f.poli("teula", [(2, 15), (8, 6), (w - 8, 6), (w - 2, 15)])
    f.rect("ferro_f", 2, 14, w - 2, 16, mode="pla")
    f.rect("llauto", 4, 19, w - 4, 20, mode="pla")
    f.rect("llauto", 4, 53, w - 4, 54, mode="pla")
    f.marca_linia((4, 58), (w - 4, 58), -1)


def _porta_ext(f, x):
    f.rect("granat_f", x, 22, x + 12, 62)
    f.rect("vidre", x + 3, 26, x + 9, 36, mode="brilla")
    f.px(x + 10, 44, MAT["llauto"][3])


def vago_ext(f, w=200):
    """Vagó de passatgers vist de fora: llenç w x 70; el carril a y=76 (les rodes les posa el joc)."""
    _cos_vago(f, w)
    _porta_ext(f, 8)
    _porta_ext(f, w - 20)
    n = 5
    pas = (w - 56) / n
    for i in range(n):
        x = int(28 + i * pas + (pas - 20) / 2)
        f.rect("ferro_f", x - 1, 23, x + 21, 45)
        f.rect("vidre", x, 24, x + 20, 44, mode="brilla")
        f.rect("vermell", x, 24, x + 3, 44, mode="pla")
        f.rect("vermell", x + 17, 24, x + 20, 44, mode="pla")
        f.rect("vermell", x, 24, x + 20, 26, mode="pla")


def furgo_ext(f, w=160):
    """El furgó de cua: porta corredissa de taulons i el llum vermell de darrere."""
    _cos_vago(f, w)
    _porta_ext(f, w - 20)
    f.rect("granat_f", 50, 24, 104, 60)
    for x in range(56, 104, 8):
        f.marca_linia((x, 25), (x, 59), -1)
    f.membre("llauto", [(52, 23), (102, 23)], 0.6, mode="pla")
    for x in (18, 116):
        f.rect("ferro_f", x - 1, 27, x + 15, 41)
        f.rect("vidre", x, 28, x + 14, 40, mode="brilla")
    f.rect("ferro_f", 0, 30, 4, 40)
    f.rect("llum_v", 0, 32, 3, 38, mode="brilla")


def estacio(f):
    """L'estació de la Llanura: 300x170, el terra de l'andén a baix. Paret de maó, porta, finestra
    il·luminada i la marquesina que surt cap a la via sobre dos pals."""
    W_, H_ = 300, 170
    f.rect("mao", 0, 46, 210, H_)
    for y in range(52, H_, 6):
        f.marca_linia((0, y), (210, y), -1)
        off = 0 if (y // 6) % 2 else 6
        for x in range(off, 210, 12):
            f.marca_linia((x, y - 6), (x, y - 1), -1)
    f.rect("pedra", 0, 160, 210, H_)
    # finestra il·luminada
    f.rect("fusta", 26, 84, 74, 130)
    f.rect("vidre", 30, 88, 70, 126, mode="brilla")
    f.rect("fusta", 49, 88, 51, 126, mode="pla")
    f.rect("fusta", 30, 106, 70, 108, mode="pla")
    f.rect("pedra", 22, 130, 78, 134)
    # porta
    f.rect("fusta", 132, 92, 170, 160)
    f.rect("granat_f", 136, 96, 166, 160)
    f.marca_linia((151, 96), (151, 160), -1)
    f.rect("vidre", 140, 100, 148, 116, mode="brilla")
    f.rect("vidre", 154, 100, 162, 116, mode="brilla")
    f.px(148, 132, MAT["llauto"][3])
    # cartell (el nom el posa el joc)
    f.rect("fusta", 80, 58, 126, 72)
    f.rect("granat_f", 82, 60, 124, 70, mode="pla")
    # marquesina
    f.poli("teula", [(0, 40), (0, 26), (W_, 34), (W_, 44)])
    for x in range(10, W_, 10):
        f.marca_linia((x, 28 + x * 8 // W_), (x, 41 + x * 4 // W_), -1)
    f.rect("fusta", 0, 44, W_ - 4, 48)
    for x in range(4, W_ - 4, 8):
        f.poli("fusta", [(x, 48), (x + 4, 48), (x + 2, 52)])
    for px in (226, 288):
        f.rect("fusta", px, 48, px + 5, H_)
        f.membre("fusta", [(px - 18, 48), (px + 2, 66)], 1.4)
        f.rect("pedra", px - 2, H_ - 4, px + 7, H_)


PECES = {"locomotora": (190, 96, locomotora), "tender": (80, 80, tender), "banc": (64, 30, banc),
         "farola": (26, 120, farola), "rellotge_estacio": (28, 34, rellotge),
         "vago_ext": (200, 70, vago_ext), "furgo_ext": (160, 70, furgo_ext), "estacio": (300, 170, estacio)}


def main():
    imatges, ancores = {}, {}
    for nom, (w, h, fn) in PECES.items():
        f = Figura(w, h, MAT, brillants=("llauto", "vidre"))
        fn(f)
        s = f.superficie(fins_a_baix=True)
        im, (ox, oy) = retallar(s)
        imatges[nom] = im
        ancores[nom] = (w // 2 - ox, h - oy)
    atles, rects = empaquetar(imatges, ample=512)
    pygame.image.save(atles, os.path.join(SORTIDA, "exterior.png"))
    with open(os.path.join(SORTIDA, "exterior.json"), "w", encoding="utf-8") as fh:
        json.dump({n: {"r": rects[n], "a": list(ancores[n])} for n in rects}, fh, separators=(",", ":"),
                  sort_keys=True)
    print(f"exterior: {len(rects)} peces, atles {atles.get_size()}")
    if len(sys.argv) > 1:
        v = pygame.Surface((760, 420))
        v.fill((30, 36, 70))
        x, y, alt = 6, 6, 0
        for im in imatges.values():
            if x + im.get_width() > 754:
                x, y, alt = 6, y + alt + 8, 0
            v.blit(im, (x, y))
            x += im.get_width() + 8
            alt = max(alt, im.get_height())
        pygame.image.save(pygame.transform.scale_by(v, 2), sys.argv[1])


if __name__ == "__main__":
    main()
