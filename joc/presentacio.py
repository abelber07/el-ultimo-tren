"""La presentació del joc: el logotip de llautó, el fons del menú (el tren creuant la plana) i l'animació inicial
a l'estació de la Llanura."""
import math
import random

import pygame

from joc.exterior import TrenExterior
from joc.mon import VIA_Y
from motor.dibuix import F_NEGRETA, F_PETITA, F_TEXT, F_TITOL, Atles, Zeta, render, text
from motor.nucli import CREMA, H, W

LLAUTO = [(62, 40, 14), (140, 100, 36), (196, 150, 58), (232, 196, 100), (255, 238, 176)]
GRANAT = (40, 14, 18)
FOSC = (18, 10, 8)


# ---------------------------------------------------------------------------------------------
# Logotip
# ---------------------------------------------------------------------------------------------
def _text_or(txt, font):
    """El text amb un degradat de llautó (clar a dalt, fosc a baix), contorn fosc i ombra."""
    pla = font.render(txt, False, (255, 255, 255))
    w, h = pla.get_size()
    blanc = pygame.Surface((w, h), pygame.SRCALPHA)          # amb alfa de debò (el render pla fa servir colorkey)
    blanc.blit(pla, (0, 0))
    grad = pygame.Surface((w, h), pygame.SRCALPHA)
    stops = [(0.0, LLAUTO[4]), (0.35, LLAUTO[3]), (0.6, LLAUTO[2]), (1.0, LLAUTO[1])]
    for y in range(h):
        t = y / max(1, h - 1)
        for (t0, c0), (t1, c1) in zip(stops, stops[1:]):
            if t0 <= t <= t1:
                k = (t - t0) / (t1 - t0)
                grad.fill(tuple(int(a + (b - a) * k) for a, b in zip(c0, c1)) + (255,), (0, y, w, 1))
                break
    grad.blit(blanc, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    vora = font.render(txt, False, FOSC)
    out = pygame.Surface((w + 4, h + 5), pygame.SRCALPHA)
    out.blit(font.render(txt, False, (0, 0, 0)), (2, 4))                  # ombra
    for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
        out.blit(vora, (2 + dx, 2 + dy))
    out.blit(grad, (2, 2))
    mascara = pygame.Surface((w + 4, h + 5), pygame.SRCALPHA)
    mascara.blit(blanc, (2, 2))
    return out, mascara


def _reblons(s, rect):
    for x in range(rect.left + 8, rect.right - 4, 24):
        for y in (rect.top + 5, rect.bottom - 6):
            pygame.draw.circle(s, LLAUTO[1], (x, y), 2)
            s.set_at((x - 1, y - 1), LLAUTO[4])


def _espiral(s, cx, cy, costat):
    """Una voluta de llautó al costat de la placa (costat: -1 esquerra, 1 dreta)."""
    pts = []
    for i in range(40):
        a = i * 0.32
        r = 2 + i * 0.28
        pts.append((cx + costat * math.cos(a) * r, cy + math.sin(a) * r))
    pygame.draw.lines(s, FOSC, False, [(x, y + 1) for x, y in pts], 3)
    pygame.draw.lines(s, LLAUTO[2], False, pts, 2)
    pygame.draw.line(s, FOSC, (cx, cy + 1), (cx - costat * 26, cy + 1), 3)
    pygame.draw.line(s, LLAUTO[3], (cx, cy), (cx - costat * 26, cy), 1)


class Logo:
    def __init__(self):
        self.text, self.mascara = _text_or("EL ÚLTIMO TREN", F_TITOL)
        tw, th = self.text.get_size()
        w, h = tw + 48, th + 20
        marge = 40
        self.surf = pygame.Surface((w + marge * 2, h + 36), pygame.SRCALPHA)
        s = self.surf
        r = pygame.Rect(marge, 22, w, h)
        cx = r.centerx
        # la placa: hexàgon allargat (puntes als costats), vores de llautó i fons granat
        P = 14

        def forma(rr, p):
            return [(rr.left, rr.top), (rr.right, rr.top), (rr.right + p, rr.centery), (rr.right, rr.bottom),
                    (rr.left, rr.bottom), (rr.left - p, rr.centery)]
        pygame.draw.polygon(s, FOSC, forma(r.inflate(6, 6), P + 2))
        pygame.draw.polygon(s, LLAUTO[1], forma(r.inflate(2, 2), P + 1))
        pygame.draw.polygon(s, LLAUTO[3], forma(r, P))
        dins = r.inflate(-6, -6)
        pygame.draw.polygon(s, LLAUTO[0], forma(dins.inflate(2, 2), P - 2))
        grad = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        for y in range(dins.height):
            k = y / dins.height
            grad.fill((int(70 - 34 * k), int(24 - 12 * k), int(26 - 12 * k), 255), (0, dins.top + y, s.get_width(), 1))
        masc = pygame.Surface(s.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(masc, (255, 255, 255, 255), forma(dins, P - 3))
        grad.blit(masc, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        s.blit(grad, (0, 0))
        pygame.draw.line(s, LLAUTO[4], (r.left + 1, r.top), (r.right - 1, r.top))
        _reblons(s, dins)
        # cresta: un arc de llautó amb la silueta d'una locomotora
        cy = r.top + 1
        pygame.draw.circle(s, FOSC, (cx, cy), 22, draw_top_left=True, draw_top_right=True)
        pygame.draw.circle(s, LLAUTO[1], (cx, cy), 20, draw_top_left=True, draw_top_right=True)
        pygame.draw.circle(s, LLAUTO[3], (cx, cy), 18, draw_top_left=True, draw_top_right=True)
        pygame.draw.line(s, LLAUTO[4], (cx - 14, cy - 11), (cx - 4, cy - 17))
        loc = FOSC
        pygame.draw.rect(s, loc, (cx - 11, cy - 9, 15, 7))                 # caldera
        pygame.draw.rect(s, loc, (cx + 3, cy - 13, 7, 11))                 # cabina
        pygame.draw.rect(s, LLAUTO[3], (cx + 5, cy - 11, 3, 3))            # finestra
        pygame.draw.rect(s, loc, (cx - 9, cy - 14, 3, 5))                  # xemeneia
        pygame.draw.rect(s, loc, (cx - 10, cy - 15, 5, 1))
        pygame.draw.polygon(s, loc, [(cx - 11, cy - 2), (cx - 15, cy - 1), (cx - 11, cy - 5)])  # llevaneu
        for x in (-7, -2, 6):
            pygame.draw.circle(s, loc, (cx + x, cy - 1), 2)
        # sota: un penjoll de llautó amb un rombe
        vy = r.bottom + 7
        pygame.draw.line(s, FOSC, (cx - 46, vy + 1), (cx + 46, vy + 1), 3)
        pygame.draw.line(s, LLAUTO[2], (cx - 46, vy), (cx + 46, vy))
        for c, m in (((cx, vy), 5), ((cx - 46, vy), 2), ((cx + 46, vy), 2)):
            pts = [(c[0] - m, c[1]), (c[0], c[1] - m), (c[0] + m, c[1]), (c[0], c[1] + m)]
            pygame.draw.polygon(s, FOSC, [(x, y + 1) for x, y in pts])
            pygame.draw.polygon(s, LLAUTO[3], pts)
        self.pos_text = (r.centerx - tw // 2, r.centery - th // 2 - 1)
        self.surf.blit(self.text, self.pos_text)
        self.t = 0

    def dibuixar(self, surf, cx, y, t):
        x = cx - self.surf.get_width() // 2
        surf.blit(self.surf, (x, y))
        # brillantor que passa per les lletres cada 5 segons
        k = (t % 300) / 60.0
        if k < 1.0:
            mw, mh = self.mascara.get_size()
            banda = pygame.Surface((mw, mh), pygame.SRCALPHA)
            bx = -40 + k * (mw + 80)
            pygame.draw.polygon(banda, (255, 250, 220, 150), [(bx, 0), (bx + 14, 0), (bx + 4, mh), (bx - 10, mh)])
            banda.blit(self.mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surf.blit(banda, (x + self.pos_text[0], y + self.pos_text[1]))


# ---------------------------------------------------------------------------------------------
# Plaques del menú
# ---------------------------------------------------------------------------------------------
def placa(surf, rect, txt, seleccionada, apagada=False):
    if seleccionada:
        pygame.draw.rect(surf, FOSC, rect.inflate(4, 4), border_radius=4)
        for y in range(rect.height):
            k = y / max(1, rect.height - 1)
            c0, c1 = LLAUTO[3], LLAUTO[1]
            col = tuple(int(a + (b - a) * k) for a, b in zip(c0, c1))
            pygame.draw.line(surf, col, (rect.left + (1 if y in (0, rect.height - 1) else 0), rect.top + y),
                             (rect.right - 1 - (1 if y in (0, rect.height - 1) else 0), rect.top + y))
        pygame.draw.line(surf, LLAUTO[4], (rect.left + 2, rect.top), (rect.right - 3, rect.top))
        im = render(txt, F_NEGRETA, (44, 22, 10))
        surf.blit(im, im.get_rect(center=(rect.centerx, rect.centery)))
        # ornaments als costats
        for costat in (-1, 1):
            x0 = rect.left - 6 if costat < 0 else rect.right + 5
            x1 = x0 + costat * 34
            pygame.draw.line(surf, LLAUTO[2], (x0, rect.centery), (x1, rect.centery))
            c = (x0 + costat * 8, rect.centery)
            pygame.draw.polygon(surf, LLAUTO[3], [(c[0] - 3, c[1]), (c[0], c[1] - 3), (c[0] + 3, c[1]),
                                                 (c[0], c[1] + 3)])
            pygame.draw.circle(surf, LLAUTO[2], (x1, rect.centery), 2)
    else:
        fons = pygame.Surface(rect.size, pygame.SRCALPHA)
        fons.fill((36, 12, 16, 215))
        surf.blit(fons, rect.topleft)
        pygame.draw.rect(surf, (110, 78, 36), rect, 1, border_radius=3)
        im = render(txt, F_TEXT, (130, 116, 100) if apagada else CREMA)
        surf.blit(im, im.get_rect(center=(rect.centerx, rect.centery)))


# ---------------------------------------------------------------------------------------------
# Fons del menú: el tren creuant la plana de nit
# ---------------------------------------------------------------------------------------------
PUJA = 26                       # quant es puja el paisatge perquè hi càpiga el menú a sota


class FonsMenu:
    def __init__(self, paisatge):
        self.paisatge = paisatge
        self.tren = TrenExterior()
        self.capa = pygame.Surface((W, H))
        self.herba = self._herba()
        self.t = 0

    def _herba(self):
        rng = random.Random(5)
        s = pygame.Surface((W * 2, 40), pygame.SRCALPHA)
        for x in range(0, W * 2, 2):
            alt = rng.randint(6, 22) if rng.random() < 0.5 else rng.randint(2, 8)
            col = rng.choice([(10, 18, 18), (14, 26, 24), (8, 14, 16)])
            inc = rng.uniform(-2, 2)
            pygame.draw.line(s, col, (x, 40), (x + inc, 40 - alt), 2)
        return s

    def actualitzar(self):
        self.t += 1
        self.paisatge.avançar(9.0)
        y = VIA_Y - PUJA
        self.tren.actualitzar(9.0, x_morro=self.x_morro(), y_carril=y)

    def x_morro(self):
        return 500 + math.sin(self.t / 90) * 6

    def dibuixar(self, surf):
        self.paisatge.dibuixar(self.capa, 0)
        surf.blit(self.capa, (0, -PUJA))
        terra = VIA_Y - PUJA + 10
        for y in range(terra, H):
            k = (y - terra) / max(1, H - terra)
            surf.fill((int(16 - 10 * k), int(22 - 12 * k), int(26 - 14 * k)), (0, y, W, 1))
        self.tren.dibuixar(surf, self.x_morro(), VIA_Y - PUJA)
        off = int(self.paisatge.despl * 1.4) % W
        surf.blit(self.herba, (-off, H - 40))


# ---------------------------------------------------------------------------------------------
# Animació inicial
# ---------------------------------------------------------------------------------------------
ANDEN_Y = 318
EST_X = 0
BANC_X = 300
FAROLA_X = 372
T_FAR = 330          # el far apareix per l'esquerra
T_ARRIBA = 470       # la locomotora entra a la pantalla
T_PARAT = 800
T_SURT = 1010
T_BUIT = 1290
T_FI = 1560
TEXTOS = [(50, 250, "Estación de la Llanura. Las doce menos dos."),
          (290, 470, "Dicen que hay un tren que solo pasa de noche."),
          (830, 1000, "Nadie sabe quién lo conduce."),
          (1310, 1490, "Nadie la vio subir.")]


class Intro:
    def __init__(self, paisatge, atles_pers):
        self.paisatge = paisatge
        self.pers = atles_pers
        self.ext = Atles("exterior")
        self.tren = TrenExterior()
        self.t = 0
        self.acabada = False
        self.efectes = []
        self.rng = random.Random(3)
        self.boira = self._boira()
        self.llum_farola = 1.0
        self.glow = self._glow(70, (90, 70, 34))
        self.glow_fin = self._glow(46, (70, 50, 20))
        lw = self.tren.atles.mida("furgo_ext")[0]
        self.llarg = self.tren.llarg()
        self.x_parat = BANC_X + self.llarg - lw / 2 + 6        # el furgó de cua s'atura davant del banc
        self.x_inici = -60
        d = self.x_parat - self.x_inici
        self.v0 = 2 * d / (T_PARAT - T_ARRIBA)
        self.frena = self.v0 / (T_PARAT - T_ARRIBA)
        self.acc = 2 * (W + 80 - (self.x_parat - self.llarg)) / (T_BUIT - 40 - T_SURT) ** 2

    def _glow(self, r, col):
        s = pygame.Surface((r * 2, r * 2))
        for i in range(r, 0, -2):
            k = (1 - i / r) ** 2
            pygame.draw.circle(s, tuple(int(c * k) for c in col), (r, r), i)
        return s

    def _boira(self):
        rng = random.Random(9)
        s = pygame.Surface((W * 2, 80), pygame.SRCALPHA)
        for _ in range(70):
            x, y = rng.randint(0, W * 2), rng.randint(30, 70)
            rx, ry = rng.randint(40, 110), rng.randint(8, 16)
            b = pygame.Surface((rx * 2, ry * 2), pygame.SRCALPHA)
            pygame.draw.ellipse(b, (150, 160, 190, 16), b.get_rect())
            for dx in (-W * 2, 0):
                s.blit(b, (x - rx + dx, y - ry))
        return s

    # --- on és el tren ----------------------------------------------------------------------
    def x_morro(self):
        t = self.t
        if t < T_ARRIBA:
            return None
        if t < T_PARAT:
            k = t - T_ARRIBA
            return self.x_inici + self.v0 * k - 0.5 * self.frena * k * k
        if t < T_SURT:
            return self.x_parat
        k = t - T_SURT
        x = self.x_parat + 0.5 * self.acc * k * k
        return x if x - self.llarg < W + 60 else None

    def vel(self):
        t = self.t
        if T_ARRIBA <= t < T_PARAT:
            return self.v0 - self.frena * (t - T_ARRIBA)
        if t >= T_SURT:
            return self.acc * (t - T_SURT)
        return 0.0

    def saltar(self):
        self.acabada = True

    def actualitzar(self):
        self.t += 1
        t = self.t
        if t >= T_FI:
            self.acabada = True
        xm = self.x_morro()
        self.tren.actualitzar(self.vel(), fum=xm is not None, x_morro=xm, y_carril=VIA_Y)
        if xm is not None and T_PARAT <= t < T_SURT and t % 9 == 0:          # vapor als peus
            for k in range(2):
                self.efectes.append(_Vapor(xm - 140 + self.rng.uniform(-10, 10), VIA_Y - 6))
        # la viatgera dorm: zetes
        if t < T_FAR + 30 and t % 70 == 0:
            self.efectes.append(Zeta(BANC_X + 8, ANDEN_Y - 40))
        self.efectes = [e for e in self.efectes if not e.actualitzar()]
        # la farola parpelleja i s'apaga quan el tren ja ha marxat
        if t > T_BUIT + 70:
            self.llum_farola = max(0.0, self.llum_farola - 0.02) if self.rng.random() < 0.7 else 0.6
        else:
            self.llum_farola = 1.0 if self.rng.random() > 0.04 else self.rng.uniform(0.2, 0.6)

    # --- dibuix ------------------------------------------------------------------------------
    def dibuixar(self, surf):
        t = self.t
        self.paisatge.dibuixar(surf, 0)
        # l'andén
        pygame.draw.rect(surf, (52, 52, 66), (0, ANDEN_Y, W, VIA_Y - ANDEN_Y - 4))
        pygame.draw.rect(surf, (96, 96, 112), (0, ANDEN_Y, W, 2))
        for x in range(0, W, 24):
            pygame.draw.line(surf, (40, 40, 52), (x, ANDEN_Y + 2), (x, VIA_Y - 5))
        # l'estació i l'atrezzo
        self.ext.dibuixar(surf, "estacio", EST_X + 150, ANDEN_Y)
        text(surf, "LLANURA", F_PETITA, (232, 196, 100), (EST_X + 103, ANDEN_Y - 105), ombra=False)
        self.ext.dibuixar(surf, "rellotge_estacio", EST_X + 196, ANDEN_Y - 88)
        self.ext.dibuixar(surf, "farola", FAROLA_X, ANDEN_Y)
        self.ext.dibuixar(surf, "banc", BANC_X, ANDEN_Y)
        surf.blit(self.glow_fin, (EST_X + 50 - 46, ANDEN_Y - 63 - 46),
                  special_flags=pygame.BLEND_RGB_ADD)
        if self.llum_farola < 0.15:
            pygame.draw.rect(surf, (30, 28, 30), (FAROLA_X - 6, ANDEN_Y - 108, 12, 12))
        # la viatgera
        if t < T_ARRIBA + 120:
            if t < T_FAR + 40:
                nom, xx, yy, girat = "seu_dorm%d" % ((t // 50) % 2), BANC_X + 2, ANDEN_Y - 8, False
            elif t < T_FAR + 110:
                nom, xx, yy, girat = "seu", BANC_X + 2, ANDEN_Y - 8, True
            else:
                nom, xx, yy, girat = "quiet0", BANC_X + 26, ANDEN_Y, True
            self.pers.dibuixar(surf, nom, xx, yy, girat=girat)
        # llum de la farola
        if self.llum_farola > 0.05:
            g = self.glow if self.llum_farola > 0.9 else self._glow(70, tuple(int(c * self.llum_farola)
                                                                                for c in (90, 70, 34)))
            surf.blit(g, (FAROLA_X - 70, ANDEN_Y - 102 - 70), special_flags=pygame.BLEND_RGB_ADD)
        # el far que s'acosta per l'esquerra
        if T_FAR <= t < T_ARRIBA + 30:
            k = min(1.0, (t - T_FAR) / (T_ARRIBA - T_FAR))
            r = int(20 + 140 * k * k)
            g = self._glow(r, (int(110 * k), int(96 * k), int(60 * k)))
            surf.blit(g, (-r + int(30 * k), VIA_Y - 64 - r), special_flags=pygame.BLEND_RGB_ADD)
        # el tren
        xm = self.x_morro()
        if xm is not None:
            sac = 1 if self.vel() > 2 and t % 4 < 2 else 0
            self.tren.dibuixar(surf, xm, VIA_Y + sac)
            if T_PARAT <= t < T_SURT:                    # el llum vermell de la cua parpelleja
                if (t // 30) % 2:
                    cua = xm - self.llarg
                    surf.blit(self.glow_fin, (cua - 46, VIA_Y - 52 - 46), special_flags=pygame.BLEND_RGB_ADD)
        for e in self.efectes:
            e.dibuixar(surf, 0)
        # boira baixa
        off = int(t * 0.3) % (W * 2)
        surf.blit(self.boira, (-off, VIA_Y - 60))
        surf.blit(self.boira, (-off + W * 2, VIA_Y - 60))
        # textos
        for t0, t1, txt in TEXTOS:
            if t0 <= t < t1:
                n = min(len(txt), (t - t0) // 2)
                a = min(1.0, (t1 - t) / 30)
                im = render(txt[:n], F_TEXT, CREMA)
                im.set_alpha(int(255 * a))
                caixa = pygame.Surface((W, 30), pygame.SRCALPHA)
                caixa.fill((0, 0, 0, int(120 * a)))
                surf.blit(caixa, (0, 22))
                surf.blit(im, (W // 2 - render(txt, F_TEXT, CREMA).get_width() // 2, 30))
        # fosa d'entrada i sortida
        alfa = 0
        if t < 60:
            alfa = 255 - t * 255 // 60
        elif t > T_FI - 70:
            alfa = min(255, (t - (T_FI - 70)) * 255 // 60)
        if alfa:
            v = pygame.Surface((W, H))
            v.set_alpha(alfa)
            surf.blit(v, (0, 0))
        if t > 30:
            text(surf, "ENTER para saltar", F_PETITA, (140, 130, 120), (W - 10, H - 10), ancora="bottomright")


class _Vapor:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-0.7, -0.2)
        self.r = random.uniform(5, 9)
        self.vida = 0
        self.max = random.randint(60, 100)

    def actualitzar(self):
        self.vida += 1
        self.x += self.vx
        self.y += self.vy
        self.r += 0.2
        return self.vida >= self.max

    def dibuixar(self, surf, cam):
        a = int(110 * (1 - self.vida / self.max))
        r = int(self.r)
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (220, 224, 236, a), (r, r), r)
        surf.blit(s, (int(self.x - cam) - r, int(self.y) - r))

