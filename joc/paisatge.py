"""El que es veu fora del tren: el cel (amb l'alba que s'acosta), les capes del paisatge i els túnels."""
import math
import random

import pygame

from joc.mon import SOSTRE_Y, TUNEL_Y, VIA_Y
from motor.nucli import H, W, ruta

AMPLE = 1280
# (nom, velocitat del tren, paral·laxi amb la càmera)
CAPES = [("nuvols", 0.06, 0.01), ("muntanyes", 0.22, 0.04), ("turons", 0.9, 0.15), ("camp", 3.6, 0.5)]
VEL_VIA = 9.0
COLOR_TUNEL = (16, 14, 20)


def _carregar(nom):
    s = pygame.image.load(ruta("assets", "img", f"paisatge_{nom}.png"))
    try:
        return s.convert_alpha() if nom != "via" else s.convert()
    except pygame.error:
        return s


def degradat(colors):
    """Superfície W x H amb un degradat vertical entre parells (y relativa, color)."""
    s = pygame.Surface((W, H))
    for y in range(H):
        t = y / (H - 1)
        for (t0, c0), (t1, c1) in zip(colors, colors[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / max(1e-6, t1 - t0)
                c = tuple(int(a + (b - a) * k) for a, b in zip(c0, c1))
                s.fill(c, (0, y, W, 1))
                break
    return s


class Paisatge:
    def __init__(self):
        self.capes = {n: _carregar(n) for n, _, _ in CAPES}
        self.via = _carregar("via")
        self.cel_nit = degradat([(0, (8, 10, 30)), (0.45, (20, 28, 70)), (0.75, (34, 50, 104)), (1, (40, 58, 110))])
        self.cel_alba = degradat([(0, (40, 40, 96)), (0.4, (150, 90, 120)), (0.7, (250, 160, 110)),
                                  (1, (255, 210, 150))])
        rng = random.Random(3)
        self.estrelles = [(rng.randrange(W), rng.randrange(0, 200), rng.random() * math.tau, rng.choice((1, 1, 2)))
                          for _ in range(90)]
        self.lluna = self._lluna()
        self.despl = 0.0           # quant ha avançat el tren (px de paisatge proper)
        self.t = 0

    def _lluna(self):
        s = pygame.Surface((60, 60), pygame.SRCALPHA)
        for r, a in ((28, 18), (22, 30), (17, 50)):
            pygame.draw.circle(s, (180, 200, 255, a), (30, 30), r)
        pygame.draw.circle(s, (226, 230, 240), (30, 30), 11)
        pygame.draw.circle(s, (250, 250, 255), (28, 28), 8)
        for cx, cy, r in ((33, 27, 2), (27, 34, 2), (35, 34, 1)):
            pygame.draw.circle(s, (196, 202, 222), (cx, cy), r)
        return s

    def avançar(self, vel):
        self.despl += vel
        self.t += 1

    def dibuixar(self, surf, cam, alba=0.0, inclinacio=0.0):
        """alba: 0 (nit) a 1 (surt el sol). inclinacio: radians que el món de fora es veu girat."""
        surf.blit(self.cel_nit, (0, 0))
        if alba > 0:
            self.cel_alba.set_alpha(int(255 * min(1.0, alba)))
            surf.blit(self.cel_alba, (0, 0))
        if alba < 0.8:
            for x, y, f, m in self.estrelles:
                b = 0.6 + 0.4 * math.sin(self.t * 0.03 + f)
                c = int(200 * b * (1 - alba))
                if c > 30:
                    surf.fill((c, c, min(255, c + 30)), (x, y, m, m))
        surf.blit(self.lluna, (520 - 30, 46 - 30 + int(alba * 80)))
        tan = math.tan(inclinacio)
        for nom, vel, par in CAPES:
            img = self.capes[nom]
            off = (self.despl * vel / VEL_VIA * 1.0 + cam * par) % AMPLE
            if abs(tan) < 0.002:
                surf.blit(img, (-off, 0))
                surf.blit(img, (AMPLE - off, 0))
            else:                                            # franges verticals desplaçades: el món inclinat
                for sx in range(0, W, 16):
                    dy = round((sx + 8 - W / 2) * tan)
                    src = (sx + off) % AMPLE
                    w = min(16, AMPLE - src)
                    surf.blit(img, (sx, dy), (src, 0, w, H))
                    if w < 16:
                        surf.blit(img, (sx + w, dy), (0, 0, 16 - w, H))
        if alba > 0:                                         # el paisatge també s'aclareix
            vel = pygame.Surface((W, VIA_Y), pygame.SRCALPHA)
            vel.fill((255, 170, 120, int(40 * alba)))
            surf.blit(vel, (0, 0))
        off = int(self.despl + cam) % 256
        for x in range(-off, W, 256):
            surf.blit(self.via, (x, VIA_Y - 4))

    def dibuixar_tunel(self, surf, sx0, sx1, portal_x=None, sortida_x=None):
        """Les columnes de pantalla [sx0, sx1) són dins el túnel: paret de pedra al fons i volta a dalt."""
        sx0, sx1 = max(0, int(sx0)), min(W, int(sx1))
        if sx1 <= sx0:
            return
        surf.fill(COLOR_TUNEL, (sx0, 0, sx1 - sx0, VIA_Y))
        off = int(self.despl * 1.6) % 48
        for y in range(TUNEL_Y + 20, VIA_Y, 16):                    # filades de maons al fons
            dx = (y // 16 % 2) * 24
            for x in range(sx0 - ((sx0 + off + dx) % 48), sx1, 48):
                pygame.draw.line(surf, (26, 24, 32), (max(sx0, x), y), (min(sx1 - 1, x + 46), y))
                if sx0 <= x < sx1:
                    pygame.draw.line(surf, (26, 24, 32), (x, y), (x, y + 15))
        surf.fill((28, 26, 34), (sx0, 0, sx1 - sx0, TUNEL_Y))       # la volta
        pygame.draw.line(surf, (60, 56, 66), (sx0, TUNEL_Y), (sx1, TUNEL_Y), 2)
        for x in range(sx0 - (sx0 + int(self.despl * 2)) % 20, sx1, 20):
            if x >= sx0:
                pygame.draw.line(surf, (40, 38, 46), (x, TUNEL_Y - 8), (x + 8, TUNEL_Y - 1))
        for px in (portal_x, sortida_x):                            # la boca del túnel
            if px is not None and -40 < px < W + 40:
                pygame.draw.rect(surf, (54, 50, 58), (px - 10, 0, 20, TUNEL_Y + 2))
                for y in range(0, TUNEL_Y, 10):
                    pygame.draw.line(surf, (34, 32, 40), (px - 10, y), (px + 10, y))
                pygame.draw.rect(surf, (80, 76, 86), (px - 12, TUNEL_Y - 4, 24, 6))


def tunel_sobre_sostre():
    return SOSTRE_Y - TUNEL_Y
