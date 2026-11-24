"""Mides del món i física comuna (cossos que cauen i xoquen amb el tren).

El tren es veu de costat, tallat com una casa de nines. Les y són de pantalla (no hi ha càmera vertical);
les x, del món: 0 és la cua del tren i el tren avança cap a la dreta.
"""
import math

import pygame

SOSTRE_Y = 104          # la superfície del sostre (s'hi pot caminar)
SOSTRE_INT = 118        # la cara de sota del sostre, per dins
TERRA_Y = 292           # el terra dels vagons
CAIXA_BAIX = 304        # on s'acaba la caixa del vagó
VIA_Y = 330             # dalt del carril
PAS = 30                # el passadís (manxa) entre vagons
MANXA_Y = 140           # dalt de la manxa
PARET = 8               # gruix de les parets dels extrems
PORTA_H = 70            # alçada del forat de les portes
TUNEL_Y = SOSTRE_Y - 24  # el sostre del túnel (dret al sostre del tren hi toques)

GRAVETAT = 0.36
VMAX_CAIGUDA = 8.0


class Cos:
    """Rectangle amb velocitat que xoca amb els sòlids i les plataformes del tren.

    x és el mig, y els peus. Les plataformes només aguanten des de dalt (es baixa amb `baixar`)."""

    ample = 14
    alt = 30

    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.a_terra = False
        self.baixant = 0              # fotogrames travessant plataformes cap avall
        self.xoc_paret = 0.0          # velocitat amb què ha topat amb una paret aquest fotograma
        self.sobre = None             # la plataforma on és

    def rect(self, alt=None):
        alt = alt or self.alt
        baix = math.ceil(self.y - 1e-6)            # qualsevol px de més ja toca el terra
        return pygame.Rect(round(self.x - self.ample / 2), baix - alt, self.ample, alt)

    def moure(self, tren, gravetat=True):
        if gravetat:
            self.vy = min(VMAX_CAIGUDA, self.vy + GRAVETAT)
        if self.baixant:
            self.baixant -= 1
        solids, plats = tren.colisions(self.x)
        self.xoc_paret = 0.0
        # eix x
        self.x += self.vx
        r = self.rect()
        for s in solids:
            if r.colliderect(s):
                if self.vx > 0:
                    self.x = s.left - self.ample / 2
                elif self.vx < 0:
                    self.x = s.right + self.ample / 2
                else:
                    continue
                self.xoc_paret = self.vx
                self.vx = 0.0
                r = self.rect()
        # eix y
        y0 = self.y
        self.y += self.vy
        self.a_terra = False
        self.sobre = None
        r = self.rect()
        for s in solids:
            if r.colliderect(s):
                if self.vy > 0:
                    self.y = s.top
                    self.a_terra = True
                elif self.vy < 0:
                    self.y = s.bottom + self.alt
                self.vy = 0.0
                r = self.rect()
        if self.vy >= 0 and not self.baixant:
            for p in plats:
                if r.left < p.right and r.right > p.left and y0 <= p.top + 0.01 and self.y >= p.top:
                    self.y = p.top
                    self.vy = 0.0
                    self.a_terra = True
                    self.sobre = p
                    r = self.rect()
                    break

    def sota_peus(self, tren):
        """Hi ha terra just a sota (per no caure dels marges)."""
        solids, plats = tren.colisions(self.x)
        r = pygame.Rect(round(self.x - 2), round(self.y), 4, 3)
        return any(r.colliderect(s) for s in solids) or any(r.colliderect(p) for p in plats)
