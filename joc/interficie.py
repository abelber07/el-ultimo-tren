"""Peces de la interfície (menú, pausa, controls, estació): un plafó blau de nit amb vora de llautó, separadors amb
un rombe i la cinta granat amb un bitllet per a l'opció triada. Tot en un sol estil perquè es vegi endreçat."""
import math

import pygame

from motor.dibuix import F_NEGRETA, F_PETITA, F_TEXT, render, text

LLAUTO = [(62, 40, 14), (140, 100, 36), (196, 150, 58), (232, 196, 100), (255, 238, 176)]
FOSC = (8, 8, 16)
NIT = (14, 18, 38)
TEXT = (222, 210, 186)
TEXT_APAGAT = (122, 116, 110)
SUAU = (160, 150, 132)
GRANAT = [(54, 14, 20), (92, 26, 30), (128, 40, 40)]
PAS = 26                            # distància entre opcions


def panell(surf, rect, alfa=200):
    """Plafó semitransparent amb doble vora fina de llautó i cantoneres."""
    r = pygame.Rect(rect)
    fons = pygame.Surface(r.size, pygame.SRCALPHA)
    for y in range(r.height):                              # una mica més clar a dalt
        k = y / max(1, r.height - 1)
        fons.fill((int(NIT[0] + 6 * (1 - k)), int(NIT[1] + 6 * (1 - k)), int(NIT[2] + 10 * (1 - k)), alfa),
                  (0, y, r.width, 1))
    surf.blit(fons, r.topleft)
    pygame.draw.rect(surf, FOSC, r.inflate(2, 2), 1)
    pygame.draw.rect(surf, LLAUTO[2], r, 1)
    pygame.draw.rect(surf, (70, 54, 30), r.inflate(-6, -6), 1)
    for cx, cy, sx, sy in ((r.left, r.top, 1, 1), (r.right - 1, r.top, -1, 1), (r.left, r.bottom - 1, 1, -1),
                           (r.right - 1, r.bottom - 1, -1, -1)):
        pygame.draw.line(surf, LLAUTO[3], (cx + sx * 2, cy + sy * 2), (cx + sx * 9, cy + sy * 2))
        pygame.draw.line(surf, LLAUTO[3], (cx + sx * 2, cy + sy * 2), (cx + sx * 2, cy + sy * 9))
        rombe(surf, cx + sx * 5, cy + sy * 5, 1, LLAUTO[4])


def rombe(surf, x, y, m, col):
    pygame.draw.polygon(surf, col, [(x - m, y), (x, y - m), (x + m, y), (x, y + m)])


def separador(surf, cx, y, ample):
    """Línia fina que s'esvaeix cap als extrems, amb un rombe al mig."""
    mig = ample // 2
    for dx in range(-mig, mig + 1):
        k = 1 - abs(dx) / mig
        a = int(160 * k ** 0.7)
        if a > 8:
            c = LLAUTO[1]
            surf.fill((c[0] * a // 255 + NIT[0] * (255 - a) // 255, c[1] * a // 255 + NIT[1] * (255 - a) // 255,
                       c[2] * a // 255 + NIT[2] * (255 - a) // 255), (cx + dx, y, 1, 1))
    rombe(surf, cx, y, 2, LLAUTO[3])


def _fer_bitllet():
    """Un bitllet de tren de llautó (24x14) amb les cantonades mossegades i una locomotora."""
    w, h = 24, 14
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(s, LLAUTO[0], (0, 0, w, h), border_radius=2)
    pygame.draw.rect(s, LLAUTO[3], (1, 1, w - 2, h - 2), border_radius=1)
    pygame.draw.rect(s, LLAUTO[2], (1, h // 2, w - 2, h // 2 - 1))
    pygame.draw.line(s, LLAUTO[4], (2, 1), (w - 3, 1))
    for cx in (0, w - 1):                                   # mossegades
        pygame.draw.circle(s, (0, 0, 0, 0), (cx, h // 2), 2)
    for y in range(3, h - 3, 2):                            # el trepat
        s.set_at((7, y), LLAUTO[0])
    loc = LLAUTO[0]                                         # la locomotora
    pygame.draw.rect(s, loc, (10, 6, 9, 4))
    pygame.draw.rect(s, loc, (16, 4, 3, 2))
    pygame.draw.rect(s, loc, (11, 4, 2, 2))
    for x in (11, 14, 17):
        s.set_at((x, 10), loc)
    s.set_at((20, 9), loc)
    return s


_BITLLET = None


def bitllet():
    global _BITLLET
    if _BITLLET is None:
        _BITLLET = _fer_bitllet()
    return _BITLLET


def cinta(surf, rect):
    """La cinta granat de l'opció triada: puntes en cua d'oreneta i vora de llautó."""
    r = pygame.Rect(rect)
    p = 6
    forma = [(r.left, r.top), (r.right, r.top), (r.right - p, r.centery), (r.right, r.bottom),
             (r.left, r.bottom), (r.left + p, r.centery)]
    s = pygame.Surface((r.width + 1, r.height + 1), pygame.SRCALPHA)
    for y in range(r.height + 1):
        k = y / max(1, r.height)
        c = GRANAT[2] if k < 0.15 else (GRANAT[1] if k < 0.75 else GRANAT[0])
        s.fill(c, (0, y, r.width + 1, 1))
    masc = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(masc, (255, 255, 255, 255), [(x - r.left, y - r.top) for x, y in forma])
    s.blit(masc, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    surf.blit(s, r.topleft)
    pygame.draw.polygon(surf, LLAUTO[2], forma, 1)
    pygame.draw.line(surf, LLAUTO[4], (r.left + 3, r.top), (r.right - 3, r.top))


def llista(surf, cx, y0, opcions, sel, t, ample=196, apagades=()):
    """Dibuixa una llista d'opcions (textos) centrada a cx i torna els rectangles de cada una (per al ratolí).

    L'opció triada va dins la cinta amb el bitllet a l'esquerra; entre opcions, separadors."""
    rects = []
    for i, txt in enumerate(opcions):
        y = y0 + i * PAS
        r = pygame.Rect(0, 0, ample, 20)
        r.center = (cx, y)
        rects.append(r)
        if i > 0:
            separador(surf, cx, y - PAS // 2, ample - 40)
        if i == sel:
            cinta(surf, r)
            b = bitllet()
            bob = round(math.sin(t / 12))
            surf.blit(b, (r.left - b.get_width() // 2 + 2, r.centery - b.get_height() // 2 + bob))
            im = render(txt, F_NEGRETA, (255, 236, 196))
            surf.blit(render(txt, F_NEGRETA, (30, 8, 10)), im.get_rect(center=(cx + 6, y + 1)))
            surf.blit(im, im.get_rect(center=(cx + 6, y)))
        else:
            col = TEXT_APAGAT if i in apagades else TEXT
            im = render(txt, F_TEXT, col)
            surf.blit(im, im.get_rect(center=(cx, y)))
    return rects


def ajuda(surf, txt, pos):
    """Línia d'ajuda de tecles, discreta."""
    text(surf, txt, F_PETITA, SUAU, pos)


def titol_panell(surf, txt, cx, y, font=F_NEGRETA):
    """Títol d'un plafó amb dues línies de llautó als costats."""
    im = render(txt, font, LLAUTO[3])
    r = im.get_rect(center=(cx, y))
    surf.blit(render(txt, font, FOSC), r.move(0, 1))
    surf.blit(im, r)
    for costat in (-1, 1):
        x0 = r.left - 8 if costat < 0 else r.right + 8
        pygame.draw.line(surf, LLAUTO[1], (x0, y), (x0 + costat * 40, y))
        rombe(surf, x0 + costat * 44, y, 2, LLAUTO[2])
