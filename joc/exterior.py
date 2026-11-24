"""El tren vist de fora (menú i animació inicial): locomotora, ténder i vagons, amb les rodes girant, les bieles,
el fum de la xemeneia i el con de llum del far."""
import math
import random

import pygame

from joc.tren import rodes
from motor.dibuix import Atles

# rodes de la locomotora respecte del mig de l'àncora (x) i del carril (y), i el radi
RODES_LOCO = [(-62, -10, 10), (-24, -14, 14), (8, -14, 14), (40, -14, 14), (70, -8, 8)]
SEPARACIO = 4


class Bufada:
    """Una bufada de fum: creix, puja una mica i es queda enrere (el vent del tren)."""

    def __init__(self, x, y, vx, vy, mida):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.r = mida
        self.vida = 0
        self.max = random.randint(110, 170)

    def actualitzar(self):
        self.vida += 1
        self.x += self.vx
        self.y += self.vy
        self.vy *= 0.985
        self.r += 0.22
        return self.vida >= self.max

    def dibuixar(self, surf):
        k = self.vida / self.max
        a = int(120 * (1 - k) ** 1.3)
        if a <= 2:
            return
        r = int(self.r)
        s = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (120, 126, 152, a // 2), (r + 1, r + 1), r)
        pygame.draw.circle(s, (176, 182, 204, a), (r + 1, r + 1), max(1, r - 2))
        pygame.draw.circle(s, (214, 218, 232, a), (r - r // 3 + 1, r - r // 3 + 1), max(1, r // 2))
        surf.blit(s, (int(self.x) - r, int(self.y) - r))


class TrenExterior:
    def __init__(self, vagons=("vago_ext", "vago_ext", "vago_ext", "furgo_ext")):
        self.atles = Atles("exterior")
        self.vagons = list(vagons)
        self.rodes = rodes(11)
        self.fum = []
        self.angle = 0.0
        self.far = self._far()

    def _far(self):
        """Con de llum del far (es pinta sumant)."""
        w, h = 260, 90
        s = pygame.Surface((w, h))
        for x in range(w):
            k = 1 - x / w
            alt = 6 + x * 0.3
            c = int(70 * k * k)
            col = (c, int(c * 0.82), int(c * 0.5))
            pygame.draw.line(s, col, (x, h / 2 - alt / 2), (x, h / 2 + alt / 2))
        return s

    def llarg(self):
        """Px des del morro de la locomotora fins a la cua."""
        w = self.atles.mida("locomotora")[0] + SEPARACIO + self.atles.mida("tender")[0]
        for v in self.vagons:
            w += SEPARACIO + self.atles.mida(v)[0]
        return w

    def actualitzar(self, vel, fum=True, x_morro=None, y_carril=None):
        """vel: px per fotograma que el tren avança respecte del terra (per girar les rodes)."""
        self.angle += vel / 14
        for b in self.fum:
            b.vx -= vel * 0.004
        self.fum = [b for b in self.fum if not b.actualitzar()]
        if fum and x_morro is not None:
            ritme = max(4, int(18 - vel * 2))
            if random.random() < 1.6 / ritme:
                lw = self.atles.mida("locomotora")[0]
                cx = x_morro - lw + 152
                self.fum.append(Bufada(cx + random.uniform(-2, 2), y_carril - 98,
                                       -vel * 0.55 - random.uniform(0.1, 0.6), -random.uniform(0.5, 1.4),
                                       random.uniform(4, 8)))

    def dibuixar(self, surf, x_morro, y_carril, far=True):
        """x_morro: x de pantalla del davant de la locomotora; el tren s'estén cap a l'esquerra."""
        for b in self.fum:
            b.dibuixar(surf)
        x = x_morro
        lw, _ = self.atles.mida("locomotora")
        loco_x = x - lw / 2
        # ténder i vagons (de davant cap a darrere)
        x -= lw + SEPARACIO
        tw, _ = self.atles.mida("tender")
        self._vehicle(surf, "tender", x - tw / 2, y_carril, (tw * 0.25, tw * 0.75))
        x -= tw + SEPARACIO
        roda = self.rodes[int(self.angle * 2) % 8]
        for v in self.vagons:
            vw, _ = self.atles.mida(v)
            pygame.draw.rect(surf, (20, 18, 26), (x - 2, y_carril - 40, SEPARACIO + 4, 20))
            self._vehicle(surf, v, x - vw / 2, y_carril, (30, 54, vw - 54, vw - 30), roda)
            x -= vw + SEPARACIO
        # locomotora
        self.atles.dibuixar(surf, "locomotora", loco_x, y_carril)
        self._rodes_loco(surf, loco_x, y_carril)
        if far:
            surf.blit(self.far, (x_morro - 6, y_carril - 64 - self.far.get_height() // 2),
                      special_flags=pygame.BLEND_RGB_ADD)

    def _vehicle(self, surf, nom, cx, y, posicions, roda=None):
        roda = roda or self.rodes[int(self.angle * 2) % 8]
        self.atles.dibuixar(surf, nom, cx, y - 8)
        w, _ = self.atles.mida(nom)
        for rx in posicions:
            surf.blit(roda, (cx - w / 2 + rx - 12, y - 23))

    def _rodes_loco(self, surf, cx, y):
        punts = []
        for rx, ry, r in RODES_LOCO:
            c = (round(cx + rx), round(y + ry))
            pygame.draw.circle(surf, (14, 14, 22), c, r)
            pygame.draw.circle(surf, (120, 92, 40), c, r, 2)
            pygame.draw.circle(surf, (40, 42, 56), c, r - 3)
            for i in range(6 if r > 9 else 4):
                a = self.angle * (14 / r) + i * math.pi / (3 if r > 9 else 2)
                p = (c[0] + math.cos(a) * (r - 3), c[1] + math.sin(a) * (r - 3))
                pygame.draw.line(surf, (20, 20, 30), c, p, 2)
            pygame.draw.circle(surf, (196, 150, 58), c, 2)
            if r == 14:
                a = self.angle
                punts.append((c[0] + math.cos(a) * 7, c[1] + math.sin(a) * 7))
        # la biela que uneix les rodes grans i el pistó cap al cilindre
        if len(punts) >= 2:
            pygame.draw.line(surf, (170, 172, 190), punts[0], punts[-1], 3)
            pygame.draw.line(surf, (90, 92, 110), punts[0], punts[-1], 1)
            pist = (round(cx + 64), round(y - 18))
            pygame.draw.line(surf, (150, 152, 170), punts[-1], pist, 2)
            for p in punts:
                pygame.draw.circle(surf, (210, 212, 226), (round(p[0]), round(p[1])), 2)
