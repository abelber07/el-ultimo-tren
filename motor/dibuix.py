"""Lletres, text, atles de sprites i efectes (partícules, textos flotants)."""
import json
import math
import random

import pygame

from motor.nucli import NEGRE, ruta

pygame.font.init()


def _font(nom, mida):
    try:
        return pygame.font.Font(ruta("assets", "fonts", nom), mida)
    except (FileNotFoundError, pygame.error):
        return pygame.font.Font(None, mida + 4)


F_PETITA = _font("Galmuri7.ttf", 8)
F_TEXT = _font("Galmuri11.ttf", 12)
F_NEGRETA = _font("Galmuri11-Bold.ttf", 12)
F_GRAN = _font("Galmuri11-Bold.ttf", 24)
F_TITOL = _font("Galmuri11-Bold.ttf", 36)

_CACHE = {}


def render(txt, font, color):
    clau = (txt, id(font), tuple(color))
    s = _CACHE.get(clau)
    if s is None:
        if len(_CACHE) > 600:
            _CACHE.clear()
        s = _CACHE[clau] = font.render(txt, False, color)
    return s


def text(surf, txt, font, color, pos, ancora="center", ombra=True, color_ombra=NEGRE):
    img = render(txt, font, color)
    r = img.get_rect(**{ancora: (round(pos[0]), round(pos[1]))})
    if ombra:
        surf.blit(render(txt, font, color_ombra), r.move(1, 1))
    surf.blit(img, r)
    return r


def text_contorn(surf, txt, font, color, pos, ancora="center", vora=NEGRE):
    img = render(txt, font, color)
    fosc = render(txt, font, vora)
    r = img.get_rect(**{ancora: (round(pos[0]), round(pos[1]))})
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (1, 1)):
        surf.blit(fosc, r.move(dx, dy))
    surf.blit(img, r)
    return r


def linies(txt, font, ample):
    out, act = [], ""
    for p in txt.split():
        prova = f"{act} {p}" if act else p
        if font.size(prova)[0] <= ample:
            act = prova
        else:
            if act:
                out.append(act)
            act = p
    if act:
        out.append(act)
    return out


def caixa(surf, rect, fons=(20, 16, 22), vora=(150, 110, 60), alfa=230):
    """Plafó de fusta fosca amb vora de llautó."""
    r = pygame.Rect(rect)
    s = pygame.Surface(r.size, pygame.SRCALPHA)
    s.fill((*fons, alfa))
    surf.blit(s, r)
    pygame.draw.rect(surf, (8, 6, 8), r, 1)
    pygame.draw.rect(surf, vora, r.inflate(-2, -2), 1)
    for cx, cy in ((r.x + 2, r.y + 2), (r.right - 3, r.y + 2), (r.x + 2, r.bottom - 3), (r.right - 3, r.bottom - 3)):
        surf.set_at((cx, cy), (255, 220, 140))


# ---------------------------------------------------------------------------------------------
# Atles
# ---------------------------------------------------------------------------------------------
class Atles:
    """Fotogrames d'un PNG + JSON fets pels generadors de tools/. Cada fotograma té una àncora (els peus)."""

    def __init__(self, nom):
        img = pygame.image.load(ruta("assets", "img", nom + ".png"))
        try:
            img = img.convert_alpha()
        except pygame.error:
            pass
        with open(ruta("assets", "img", nom + ".json"), encoding="utf-8") as fh:
            dades = json.load(fh)
        self.fot = {}
        self.anc = {}
        for n, d in dades.items():
            self.fot[n] = img.subsurface(pygame.Rect(d["r"]))
            self.anc[n] = tuple(d["a"])
        self._girats = {}

    def afegir(self, altre, noms):
        """Fa servir també fotogrames d'un altre atles."""
        for n in noms:
            self.fot[n], self.anc[n] = altre.fot[n], altre.anc[n]

    def __contains__(self, nom):
        return nom in self.fot

    def mida(self, nom):
        return self.fot[nom].get_size()

    def imatge(self, nom, girat=False):
        if not girat:
            return self.fot[nom]
        s = self._girats.get(nom)
        if s is None:
            s = self._girats[nom] = pygame.transform.flip(self.fot[nom], True, False)
        return s

    def dibuixar(self, surf, nom, x, y, girat=False, alfa=None, blanc=False):
        """Dibuixa el fotograma amb l'àncora a (x, y). girat: mira a l'esquerra."""
        img = self.imatge(nom, girat)
        ax, ay = self.anc[nom]
        if girat:
            ax = img.get_width() - ax
        if blanc:
            img = silueta(img)
        if alfa is not None:
            img = img.copy()
            img.set_alpha(alfa)
        surf.blit(img, (round(x - ax), round(y - ay)))


_SILUETES = {}


def silueta(img, color=(255, 255, 255)):
    clau = (id(img), color)
    s = _SILUETES.get(clau)
    if s is None:
        m = pygame.mask.from_surface(img)
        s = _SILUETES[clau] = m.to_surface(setcolor=(*color, 255), unsetcolor=(0, 0, 0, 0))
    return s


# ---------------------------------------------------------------------------------------------
# Efectes (coordenades del món)
# ---------------------------------------------------------------------------------------------
class Particula:
    __slots__ = ("x", "y", "vx", "vy", "color", "vida", "t", "mida", "grav", "frec")

    def __init__(self, x, y, vx, vy, color, vida=25, mida=2.0, grav=0.0, frec=0.96):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.color, self.vida, self.t, self.mida, self.grav, self.frec = color, vida, 0, mida, grav, frec

    def actualitzar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.grav
        self.vx *= self.frec
        self.vy *= self.frec
        self.t += 1
        return self.t >= self.vida

    def dibuixar(self, surf, cx):
        r = self.mida * (1 - self.t / self.vida)
        x, y = int(self.x - cx), int(self.y)
        if r < 1.2:
            if r > 0.3:
                surf.set_at((x, y), self.color) if 0 <= x < surf.get_width() and 0 <= y < surf.get_height() else None
        else:
            pygame.draw.rect(surf, self.color, (x - int(r) // 2, y - int(r) // 2, int(r), int(r)))


class TextFlotant:
    def __init__(self, x, y, txt, color, font=None, vida=50):
        self.x, self.y, self.t, self.vida = x, y, 0, vida
        self.txt, self.color, self.font = txt, color, font or F_NEGRETA

    def actualitzar(self):
        self.y -= 0.5
        self.t += 1
        return self.t >= self.vida

    def dibuixar(self, surf, cx):
        if self.t > self.vida - 10 and self.t % 2:
            return
        text_contorn(surf, self.txt, self.font, self.color, (self.x - cx, self.y))


class Zeta:
    """Les zetes de qui dorm."""

    def __init__(self, x, y):
        self.x, self.y, self.t, self.vida = x, y, 0, 90
        self.fase = random.uniform(0, math.tau)

    def actualitzar(self):
        self.t += 1
        self.y -= 0.25
        return self.t >= self.vida

    def dibuixar(self, surf, cx):
        x = self.x - cx + math.sin(self.t * 0.07 + self.fase) * 3
        mida = F_PETITA if self.t < 45 else F_TEXT
        text(surf, "z", mida, (200, 206, 240), (x, self.y), ombra=True)


def esclat(efectes, x, y, n, colors, vel=(1, 3), mida=(2, 4), vida=(14, 30), grav=0.0):
    for _ in range(n):
        a = random.uniform(0, math.tau)
        v = random.uniform(*vel)
        efectes.append(Particula(x, y, math.cos(a) * v, math.sin(a) * v, random.choice(colors),
                                 random.randint(*vida), random.uniform(*mida), grav))


def fum(efectes, x, y, n=10):
    colors = [(70, 68, 80), (100, 98, 110), (140, 138, 150)]
    for _ in range(n):
        efectes.append(Particula(x + random.uniform(-8, 8), y + random.uniform(-10, 6), random.uniform(-0.6, 0.6),
                                 random.uniform(-1.2, -0.2), random.choice(colors), random.randint(20, 40),
                                 random.uniform(3, 6), -0.01, 0.95))
