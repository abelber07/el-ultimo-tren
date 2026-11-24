"""Genera les capes del paisatge nocturn (tram 1: la plana) a assets/img/paisatge_*.png.

    python tools/generar_paisatge.py [vista.png]

Capes horitzontals que es repeteixen (ample AMPLE, totes periòdiques): núvols, muntanyes, turons amb granges i
molins, el camp de blat amb pals de telègraf, i la via. El cel (degradat, estrelles i lluna) el pinta el joc.
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402
from pintor import Figura  # noqa: E402

pygame.init()
AQUI = os.path.dirname(os.path.abspath(__file__))
SORTIDA = os.path.join(AQUI, "..", "assets", "img")
AMPLE = 1280
H = 360
LLUM = (255, 200, 110)
LLUM_F = (200, 120, 60)


def ona(x, termes):
    """Suma de sinus periòdica en AMPLE: termes = [(freqüència entera, amplitud, fase)]."""
    return sum(a * math.sin(math.tau * f * x / AMPLE + p) for f, a, p in termes)


def termes(rng, n, f0, f1, a0):
    return [(rng.randint(f0, f1), a0 * rng.uniform(0.4, 1.0) / (1 + i * 0.6), rng.uniform(0, math.tau))
            for i in range(n)]


def wrap_blit(s, img, x, y):
    s.blit(img, (x, y))
    if x + img.get_width() > AMPLE:
        s.blit(img, (x - AMPLE, y))
    if x < 0:
        s.blit(img, (x + AMPLE, y))


# ---------------------------------------------------------------------------------------------
def nuvols(rng):
    s = pygame.Surface((AMPLE, 110), pygame.SRCALPHA)
    cols = [(30, 40, 92), (40, 54, 112), (54, 70, 132)]
    for _ in range(9):
        cx, cy = rng.randrange(AMPLE), rng.randint(20, 80)
        w = rng.randint(50, 110)
        blocs = []
        for i in range(rng.randint(5, 9)):
            bx = cx + rng.randint(-w // 2, w // 2)
            bw = rng.randint(18, 44)
            bh = rng.randint(6, 14)
            blocs.append((bx, cy - rng.randint(0, 10), bw, bh))
        for k, col in enumerate(cols):
            for bx, by, bw, bh in blocs:
                r = pygame.Rect(bx - bw // 2 + k * 2, by - k * 2 + 2, bw - k * 4, bh - k)
                if r.w > 2 and r.h > 1:
                    for dx in (0, -AMPLE, AMPLE):
                        pygame.draw.rect(s, col, r.move(dx, 0), border_radius=4)
    return s


def muntanyes(rng):
    s = pygame.Surface((AMPLE, H), pygame.SRCALPHA)
    base = 198
    # serralada de pics: suma d'ones triangulars periòdiques (cims punxeguts)
    pics = [(rng.randint(4, 6), 40, rng.uniform(0, 1)), (rng.randint(10, 13), 18, rng.uniform(0, 1))]

    def tri(x, f, fase):
        u = (x * f / AMPLE + fase) % 1.0
        return 1 - 2 * abs(u - 0.5)

    cims = [base - 8 - sum(a * tri(x, f, fs) for f, a, fs in pics) for x in range(AMPLE)]
    cos, fosc = (34, 46, 102), (26, 36, 82)
    neu, neu_f = (156, 170, 218), (96, 112, 172)
    for x in range(AMPLE):
        y = int(cims[x])
        pend = cims[(x + 1) % AMPLE] - cims[x - 1]
        ombra = pend < 0                                   # la lluna és a la dreta: els vessants d'esquerra, foscos
        pygame.draw.line(s, fosc if ombra else cos, (x, y), (x, base + 20))
        if y < base - 52:
            alt_neu = int((base - 52 - y) * 0.7) + 2
            pygame.draw.line(s, neu_f if ombra else neu, (x, y), (x, y + alt_neu))
    # boira baixa
    for y in range(base - 6, base + 20):
        a = max(0, int(110 * (y - base + 6) / 26))
        pygame.draw.line(s, (40, 56, 108, a), (0, y), (AMPLE, y))
    return s


def molí(fase):
    mat = {"pedra": [(14, 18, 30), (36, 42, 60), (52, 58, 80), (70, 78, 102), (96, 104, 130)],
           "fusta": [(16, 12, 14), (42, 34, 36), (60, 50, 50), (82, 70, 68), (110, 96, 92)]}
    f = Figura(34, 40, mat)
    f.poli("pedra", [(13, 16), (21, 16), (23, 39), (11, 39)])
    f.poli("fusta", [(12, 17), (17, 11), (22, 17)])
    for k in range(4):
        a = fase + k * math.pi / 2
        p0 = (17, 15)
        p1 = (17 + math.cos(a) * 14, 15 + math.sin(a) * 14)
        f.membre("fusta", [p0, p1], 0.7, mode="pla")
        q = (17 + math.cos(a) * 9 + math.cos(a + 1.57) * 3, 15 + math.sin(a) * 9 + math.sin(a + 1.57) * 3)
        f.membre("fusta", [p1, q], 1.4, mode="pla")
    s = f.superficie()
    s.set_at((17, 30), LLUM)
    s.set_at((17, 31), LLUM_F)
    return s


def granja(rng):
    mat = {"paret": [(14, 18, 28), (40, 40, 56), (58, 56, 74), (78, 74, 94), (104, 100, 120)],
           "teulada": [(12, 10, 18), (34, 26, 40), (50, 38, 54), (68, 52, 70), (92, 72, 92)]}
    w = rng.randint(22, 34)
    f = Figura(w + 6, 26, mat)
    f.poli("teulada", [(1, 12), (w // 2 + 3, 3), (w + 5, 12)])
    f.rect("paret", 3, 12, w + 3, 25)
    s = f.superficie()
    for i in range(rng.randint(1, 3)):
        x = 6 + i * 7
        if x + 2 < w and rng.random() < 0.8:
            pygame.draw.rect(s, LLUM, (x, 16, 3, 3))
            s.set_at((x + 1, 18), LLUM_F)
    if rng.random() < 0.6:                                     # xemeneia
        pygame.draw.rect(s, mat["paret"][1], (w - 2, 3, 3, 6))
    return s


def turons(rng):
    s = pygame.Surface((AMPLE, H), pygame.SRCALPHA)
    capes = [(214, (22, 44, 62), (30, 58, 72), 14), (232, (18, 38, 52), (26, 52, 62), 10)]
    perfils = []
    for base, col, llum, amp in capes:
        t = termes(rng, 5, 2, 10, amp)
        perfil = [base + ona(x, t) for x in range(AMPLE)]
        perfils.append(perfil)
        for x in range(AMPLE):
            y = int(perfil[x])
            pend = perfil[(x + 1) % AMPLE] - perfil[x - 1]
            pygame.draw.line(s, col, (x, y), (x, H))
            pygame.draw.line(s, llum if pend > 0.15 else col, (x, y), (x, y + 2))
        # solcs dels camps (línies suaus) i bardisses
        for _ in range(26):
            x0 = rng.randrange(AMPLE)
            for k in range(rng.randint(20, 60)):
                x = (x0 + k) % AMPLE
                y = int(perfil[x]) + 6 + (k // 7) % 3 * 4
                if y < H:
                    s.set_at((x, y), llum)
        for _ in range(40):                                    # arbres rodons
            x = rng.randrange(AMPLE)
            y = int(perfil[x])
            r = rng.randint(3, 6)
            for dx in (0, -AMPLE, AMPLE):
                pygame.draw.circle(s, (12, 28, 36), (x + dx, y - r + 2), r)
                pygame.draw.circle(s, (18, 38, 46), (x + dx - 1, y - r + 1), max(1, r - 2))
        for _ in range(14):                                    # xiprers
            x = rng.randrange(AMPLE)
            y = int(perfil[x])
            h = rng.randint(10, 18)
            for dx in (0, -AMPLE, AMPLE):
                pygame.draw.ellipse(s, (10, 24, 32), (x + dx - 2, y - h, 5, h + 2))
    # granges i molins sobre la primera capa
    perfil = perfils[0]
    xs = sorted(rng.sample(range(40, AMPLE - 40, 20), 9))
    for i, x in enumerate(xs):
        y = int(perfil[x]) + 3
        if i % 3 == 1:
            img = molí(rng.uniform(0, 1.5))
        else:
            img = granja(rng)
        wrap_blit(s, img, x - img.get_width() // 2, y - img.get_height())
    return s


def camp(rng):
    s = pygame.Surface((AMPLE, H), pygame.SRCALPHA)
    top = 262
    blat = [(70, 54, 34), (104, 80, 44), (138, 106, 56), (170, 134, 70), (204, 168, 96)]
    # massa del blat amb espigues
    for x in range(AMPLE):
        y = top + int(ona(x, [(20, 2, 0.3), (47, 1.5, 1.1)]))
        pygame.draw.line(s, blat[1], (x, y), (x, H))
        pygame.draw.line(s, blat[0], (x, y + 30), (x, H))
    for _ in range(2200):
        x = rng.randrange(AMPLE)
        y = rng.randint(top - 4, top + 40)
        c = blat[2] if y > top + 8 else blat[3]
        if rng.random() < 0.15:
            c = blat[4]
        l = rng.randint(2, 5)
        dx = rng.choice((0, 1))
        pygame.draw.line(s, c, (x, y), ((x + dx) % AMPLE, y + l))
    # tanca
    for x in range(0, AMPLE, 32):
        pygame.draw.rect(s, (34, 22, 18), (x, top + 18, 3, 22))
        pygame.draw.line(s, (70, 46, 32), (x, top + 18), (x, top + 38))
    for y in (top + 22, top + 30):
        pygame.draw.line(s, (40, 26, 20), (0, y), (AMPLE, y))
        pygame.draw.line(s, (78, 52, 36), (0, y - 1), (AMPLE, y - 1))
    # vorera d'herba fosca
    for x in range(AMPLE):
        y = top + 38 + int(ona(x, [(64, 1.5, 0), (13, 2, 2)]))
        pygame.draw.line(s, (16, 30, 26), (x, y), (x, H))
    # pals de telègraf amb fils
    pals = list(range(100, AMPLE, 320))
    for x in pals:
        pygame.draw.rect(s, (30, 18, 14), (x - 2, 96, 5, top + 40 - 96))
        pygame.draw.line(s, (76, 48, 32), (x - 1, 96), (x - 1, top + 40))
        pygame.draw.rect(s, (36, 22, 16), (x - 14, 104, 29, 4))
        pygame.draw.line(s, (84, 54, 36), (x - 14, 104), (x + 14, 104))
        for ix in (-12, -5, 5, 12):
            pygame.draw.rect(s, (150, 160, 170), (x + ix - 1, 101, 2, 3))
    for i, x in enumerate(pals):
        x2 = pals[(i + 1) % len(pals)] + (AMPLE if i == len(pals) - 1 else 0)
        for ix in (-12, -5, 5, 12):
            a, b = x + ix, x2 + ix
            for k in range(b - a):
                t = k / (b - a)
                y = 101 + int(math.sin(t * math.pi) * 14)
                s.set_at(((a + k) % AMPLE, y), (24, 28, 40))
    return s


def via(rng):
    """La franja de sota el tren: travesses, carrils i grava (de y = 0 a 40)."""
    s = pygame.Surface((256, 40))
    s.fill((26, 22, 30))
    for _ in range(900):
        x, y = rng.randrange(256), rng.randrange(40)
        s.set_at((x, y), rng.choice([(46, 40, 50), (60, 54, 62), (36, 32, 40), (80, 74, 82)]))
    for x in range(0, 256, 16):
        pygame.draw.rect(s, (44, 28, 22), (x, 6, 11, 8))
        pygame.draw.line(s, (70, 46, 34), (x, 6), (x + 10, 6))
    pygame.draw.rect(s, (70, 72, 84), (0, 3, 256, 3))
    pygame.draw.line(s, (150, 152, 166), (0, 3), (256, 3))
    return s


def main():
    rng = random.Random(7)
    capes = {"nuvols": nuvols(rng), "muntanyes": muntanyes(rng), "turons": turons(rng), "camp": camp(rng),
             "via": via(rng)}
    os.makedirs(SORTIDA, exist_ok=True)
    for nom, s in capes.items():
        pygame.image.save(s, os.path.join(SORTIDA, f"paisatge_{nom}.png"))
    print("paisatge: " + ", ".join(capes))
    if len(sys.argv) > 1:
        v = pygame.Surface((AMPLE, H))
        for y in range(H):
            k = y / H
            v.fill((int(10 + 24 * k), int(14 + 34 * k), int(40 + 60 * k)), (0, y, AMPLE, 1))
        for nom in ("nuvols", "muntanyes", "turons", "camp"):
            v.blit(capes[nom], (0, 0))
        for x in range(0, AMPLE, 256):
            v.blit(capes["via"], (x, 326))
        pygame.image.save(pygame.transform.scale_by(v, 2), sys.argv[1])


if __name__ == "__main__":
    main()
