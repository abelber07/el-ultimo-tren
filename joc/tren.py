"""El tren d'un tram: els vagons (generats a l'atzar), les seves col·lisions i com es pinten.

Cada vagó té un tipus (`TIPUS`) i en generar-se omple: mobles (decorat fix, pintat un sol cop dins la
superfície del vagó), plataformes i sòlids, finestres, llums, escotilles amb escala, on surten els enemics
(`spawns`) i els objectes (`objectes`). La porta del davant de cada vagó és tancada fins que no queden
enemics desperts a dins; la del darrere sempre és oberta (menys la de la cua del tren).
"""
import math
import random

import pygame

from joc.mon import (CAIXA_BAIX, MANXA_Y, PARET, PAS, PORTA_H, SOSTRE_INT, SOSTRE_Y, TERRA_Y, VIA_Y)

DALT = SOSTRE_Y - 14            # on comença la superfície pintada del vagó
RACK_Y = 176                    # portaequipatges
FIN_Y0, FIN_Y1 = 186, 246       # finestres

# paleta de cada tipus: paret, paret fosca, sòcol, motllura
PALETES = {
    "cua": ((74, 40, 28), (56, 30, 22), (40, 20, 14), (150, 106, 50)),
    "segona": ((78, 42, 28), (60, 32, 22), (42, 22, 14), (164, 118, 56)),
    "llitera": ((32, 52, 46), (24, 40, 36), (40, 24, 18), (150, 120, 70)),
    "restaurant": ((92, 32, 34), (70, 24, 26), (46, 24, 16), (190, 146, 70)),
    "equipatges": ((58, 46, 36), (46, 36, 28), (36, 28, 22), (90, 76, 60)),
    "correu": ((46, 50, 58), (36, 40, 48), (36, 28, 22), (110, 100, 80)),
    "venedor": ((70, 36, 58), (54, 28, 44), (40, 22, 18), (190, 150, 80)),
}
NOMS = {"cua": "Furgón de cola", "segona": "Segunda clase", "llitera": "Coche cama",
        "restaurant": "Vagón restaurante", "equipatges": "Vagón de equipajes", "correu": "Vagón correo",
        "venedor": "La máquina"}
CAIXA_EXT = (74, 22, 26)          # el color de fora del vagó (granat)
CAIXA_EXT_C = (120, 40, 40)
SOSTRE_C = (58, 64, 88)
SOSTRE_CL = (110, 118, 148)


class Vago:
    def __init__(self, idx, tipus, x0, ample, rng, dificultat):
        self.idx, self.tipus = idx, tipus
        self.x0, self.ample = x0, ample
        self.x1 = x0 + ample
        self.dificultat = dificultat
        self.mobles = []          # (nom, x, y, girat) al món, peus a (x, y)
        self.plats = []           # pygame.Rect (només per dalt)
        self.blocs = []           # sòlids extra (caixes)
        self.finestres = []       # (x, w)
        self.llums = []           # (x, y, nom)
        self.escotilles = []      # x del mig
        self.racks = []           # (x0, x1)
        self.spawns = []          # (tipus, x, y, opcions)
        self.objectes = []        # (tipus, x, y)
        self.cartells = []        # (x, y, text)
        self.oberta = True        # porta del davant
        self.visitat = False
        self.surf = None
        GENERADORS[tipus](self, rng)
        self._fer_colisions()

    @property
    def nom(self):
        return NOMS.get(self.tipus, self.tipus)

    def ix(self, a, b):
        """Interval útil de l'interior."""
        return self.x0 + PARET + a, self.x1 - PARET - b

    # --- col·lisions -------------------------------------------------------------------------
    def _fer_colisions(self):
        s = []
        # sostre (amb forats a les escotilles)
        trams = [(self.x0, self.x1)]
        for ex in sorted(self.escotilles):
            nous = []
            for a, b in trams:
                if a < ex - 14 < b:
                    nous += [(a, ex - 14), (ex + 14, b)]
                else:
                    nous.append((a, b))
            trams = nous
        for a, b in trams:
            s.append(pygame.Rect(a, SOSTRE_Y, b - a, SOSTRE_INT - SOSTRE_Y))
        for ex in self.escotilles:
            self.plats.append(pygame.Rect(ex - 14, SOSTRE_Y, 28, 4))
        # parets dels extrems (per sobre de la porta)
        s.append(pygame.Rect(self.x0, SOSTRE_Y, PARET, TERRA_Y - PORTA_H - SOSTRE_Y))
        s.append(pygame.Rect(self.x1 - PARET, SOSTRE_Y, PARET, TERRA_Y - PORTA_H - SOSTRE_Y))
        if self.idx == 0:                                       # la cua: paret sencera
            s.append(pygame.Rect(self.x0, SOSTRE_Y - 300, PARET, TERRA_Y - SOSTRE_Y + 300))
        s += self.blocs
        self.solids = s
        self.porta_rect = pygame.Rect(self.x1 - PARET, TERRA_Y - PORTA_H, PARET, PORTA_H)

    def escala_a(self, x, y):
        """L'escotilla amb escala a tocar de (x, y) o None."""
        for ex in self.escotilles:
            if abs(x - ex) < 10 and SOSTRE_Y - 34 < y <= TERRA_Y + 1:
                return ex
        return None


# ---------------------------------------------------------------------------------------------
# Generadors de cada tipus de vagó
# ---------------------------------------------------------------------------------------------
def _finestres_i_llums(v, xs, w=58, llums=True):
    for cx in xs:
        v.finestres.append((cx - w // 2, w))
    if llums:
        for a, b in zip(xs, xs[1:]):
            v.llums.append(((a + b) // 2, 214, "llum"))


def _escotilla(v, rng, prob, candidats):
    if candidats and rng.random() < prob:
        v.escotilles.append(rng.choice(candidats))


def _maleta(v, rng, x, y, viva_prob):
    if rng.random() < viva_prob:
        v.spawns.append(("maleta", x, y, {}))
    else:
        v.objectes.append(("maleta", x, y))


def gen_cua(v, rng):
    """El furgó de cua: aquí es desperta la viatgera. Bancs, cartells amb els controls i una escotilla."""
    a, b = v.ix(0, 0)
    _finestres_i_llums(v, [a + 120, a + 300, a + 480], w=64)
    for x in (a + 60, a + 240, a + 420):
        v.mobles.append(("seient", x, TERRA_Y, False))
        v.plats.append(pygame.Rect(x - 7, TERRA_Y - 19, 20, 4))
    v.escotilles.append(a + 540)
    v.cartells += [(a + 120, 150, "A / D  moverte     ESPACIO  saltar"),
                   (a + 300, 150, "J  golpe     K  abrir el paraguas"),
                   (a + 456, 150, "MAYÚS  voltereta    E  coger"),
                   (a + 506, 236, "W  subir al techo")]
    v.objectes.append(("maleta", a + 200, TERRA_Y))
    v.objectes.append(("bitllet", a + 330, TERRA_Y - 2))


def gen_segona(v, rng):
    a, b = v.ix(10, 10)
    badies = list(range(a, b - 119, 124))
    xs = []
    for bx in badies:
        v.mobles.append(("seient", bx + 14, TERRA_Y, False))
        v.mobles.append(("tauleta", bx + 62, TERRA_Y, False))
        v.mobles.append(("seient", bx + 110, TERRA_Y, True))
        for sx, gir in ((bx + 14, False), (bx + 110, True)):
            v.plats.append(pygame.Rect(sx - 13 if gir else sx - 7, TERRA_Y - 19, 20, 4))
            v.plats.append(pygame.Rect(sx + 2 if gir else sx - 15, TERRA_Y - 38, 13, 4))
        v.plats.append(pygame.Rect(bx + 54, TERRA_Y - 24, 16, 4))
        xs.append(bx + 62)
        v.racks.append((bx + 26, bx + 98))
        v.plats.append(pygame.Rect(bx + 26, RACK_Y, 72, 4))
        if rng.random() < 0.7:
            _maleta(v, rng, bx + rng.randint(40, 84), RACK_Y, 0.25 + 0.1 * v.dificultat)
    _finestres_i_llums(v, xs)
    n = 2 + v.dificultat + rng.randint(0, 1)
    for i in range(n):
        v.spawns.append(("sense_cara", rng.randint(a + 140, b - 30), TERRA_Y, {}))
    if rng.random() < 0.5:
        v.objectes.append(("ampolla", rng.choice(xs) + 2, TERRA_Y - 24))
    _escotilla(v, rng, 0.55, [bx + 62 for bx in badies[1:]])


def gen_llitera(v, rng):
    a, b = v.ix(10, 10)
    comps = list(range(a, b - 150, 160))
    xs = []
    for cx in comps:
        v.mobles.append(("llitera", cx + 44, TERRA_Y - 40 + 15, False))
        v.mobles.append(("llitera", cx + 44, TERRA_Y - 92 + 15, False))
        v.plats.append(pygame.Rect(cx + 6, TERRA_Y - 40, 76, 4))
        v.plats.append(pygame.Rect(cx + 6, TERRA_Y - 92, 76, 4))
        xs.append(cx + 124)
        for nivell in (TERRA_Y - 40, TERRA_Y - 92):
            if rng.random() < 0.55:
                v.spawns.append(("sense_cara", cx + 46, nivell, {"dorm": True}))
    for cx in xs:
        v.finestres.append((cx - 20, 40))
    for cx in comps:
        v.llums.append((cx + 44, 150, "llum"))
    for _ in range(rng.randint(0, 1 + v.dificultat // 2)):
        v.spawns.append(("sense_cara", rng.randint(a + 150, b - 30), TERRA_Y, {"dorm": rng.random() < 0.5}))
    if rng.random() < 0.6:
        v.objectes.append(("pa", rng.choice(comps) + 70, TERRA_Y - 92))
    _escotilla(v, rng, 0.5, xs[1:])


def gen_restaurant(v, rng):
    a, b = v.ix(20, 20)
    taules = list(range(a + 30, b - 40, 110))
    for tx in taules:
        v.mobles.append(("cadira", tx - 32, TERRA_Y, False))
        v.mobles.append(("taula", tx, TERRA_Y, False))
        v.mobles.append(("cadira", tx + 32, TERRA_Y, True))
        v.plats.append(pygame.Rect(tx - 23, TERRA_Y - 20, 46, 4))
        v.llums.append((tx, SOSTRE_INT + 22, "llum_penjant"))
        if rng.random() < 0.4:
            v.objectes.append(("pa", tx - 12, TERRA_Y - 20))
        elif rng.random() < 0.4:
            v.objectes.append(("ampolla", tx + 14, TERRA_Y - 20))
    _finestres_i_llums(v, [tx + 55 for tx in taules[:-1]], w=70, llums=False)
    n = 2 + v.dificultat
    for i in range(n):
        v.spawns.append((rng.choice(["sense_cara", "sense_cara", "polisso"]), rng.randint(a + 120, b - 20),
                         TERRA_Y, {}))
    _escotilla(v, rng, 0.5, [tx + 55 for tx in taules[1:-1]])


def gen_equipatges(v, rng):
    a, b = v.ix(30, 30)
    x = a + 60
    while x < b - 60:
        alt = rng.choice((1, 1, 2, 2, 3))
        n = rng.choice((1, 2))
        w = 26 * n
        for k in range(alt):
            for j in range(n):
                v.mobles.append(("caixa", x + 13 + j * 26, TERRA_Y - k * 24, False))
        v.blocs.append(pygame.Rect(x, TERRA_Y - alt * 24, w, alt * 24))
        if rng.random() < 0.6:
            _maleta(v, rng, x + w // 2, TERRA_Y - alt * 24, 0.35 + 0.1 * v.dificultat)
        x += w + rng.randint(50, 90)
    for _ in range(rng.randint(2, 4)):
        _maleta(v, rng, rng.randint(a + 30, b - 30), TERRA_Y, 0.4)
    v.objectes.append(("bagul", rng.randint(a + 100, b - 40), TERRA_Y))
    for cx in range(a + 80, b - 40, 180):
        v.finestres.append((cx - 10, 20))
    v.llums.append(((a + b) // 2, SOSTRE_INT + 22, "llum_penjant"))


def gen_correu(v, rng):
    a, b = v.ix(20, 20)
    x = a + 40
    while x < b - 120:
        w = rng.randint(70, 110)
        y = rng.choice((TERRA_Y - 56, RACK_Y + 10))
        v.plats.append(pygame.Rect(x, y, w, 4))
        v.racks.append((x, x + w, y))
        x += w + rng.randint(40, 80)
    for _ in range(rng.randint(4, 7)):
        v.mobles.append(("saca", rng.randint(a + 20, b - 20), TERRA_Y, rng.random() < 0.5))
    for _ in range(1 + v.dificultat):
        v.spawns.append(("polisso", rng.randint(a + 160, b - 30), TERRA_Y, {}))
    for _ in range(rng.randint(0, 2)):
        v.spawns.append(("sense_cara", rng.randint(a + 200, b - 30), TERRA_Y, {}))
    for cx in range(a + 100, b - 40, 200):
        v.finestres.append((cx - 16, 32))
        v.llums.append((cx + 60, 200, "llum"))
    v.objectes.append(("bitllet", rng.randint(a + 60, b - 60), TERRA_Y - 2))
    _escotilla(v, rng, 0.6, [a + 300])


def gen_venedor(v, rng):
    a, b = v.ix(20, 20)
    cx = (a + b) // 2
    v.mobles.append(("maquina", cx, TERRA_Y, False))
    v.mobles.append(("seient", a + 50, TERRA_Y, False))
    v.mobles.append(("seient", b - 50, TERRA_Y, True))
    v.plats.append(pygame.Rect(a + 43, TERRA_Y - 19, 20, 4))
    v.plats.append(pygame.Rect(b - 63, TERRA_Y - 19, 20, 4))
    v.objectes += [("venda_pa", cx - 80, TERRA_Y), ("venda_cor", cx + 80, TERRA_Y)]
    _finestres_i_llums(v, [a + 110, b - 110], w=60, llums=False)
    v.llums.append((cx, SOSTRE_INT + 22, "llum_penjant"))


GENERADORS = {"cua": gen_cua, "segona": gen_segona, "llitera": gen_llitera, "restaurant": gen_restaurant,
              "equipatges": gen_equipatges, "correu": gen_correu, "venedor": gen_venedor}
AMPLES = {"cua": 640, "segona": 820, "llitera": 820, "restaurant": 760, "equipatges": 760, "correu": 720,
          "venedor": 560}


def ordre_vagons(rng, n=7):
    """La cua, després vagons barrejats (sense repetir seguits) i la màquina expenedora cap al mig."""
    tipus = ["segona", "llitera", "restaurant", "equipatges", "correu"]
    seq = []
    while len(seq) < n - 2:
        bossa = tipus[:]
        rng.shuffle(bossa)
        if seq and bossa[0] == seq[-1]:
            bossa.append(bossa.pop(0))
        seq += bossa
    seq = seq[:n - 2]
    seq.insert(len(seq) // 2 + 1, "venedor")
    return ["cua"] + seq


# ---------------------------------------------------------------------------------------------
class Tren:
    def __init__(self, llavor, n=7):
        rng = random.Random(llavor)
        self.vagons = []
        x = 0
        for i, t in enumerate(ordre_vagons(rng, n)):
            dif = min(3, i // 2)
            v = Vago(i, t, x, AMPLES[t], rng, dif)
            self.vagons.append(v)
            x = v.x1 + PAS
        self.llarg = self.vagons[-1].x1
        self.terra = pygame.Rect(-400, TERRA_Y, self.llarg + 800, 80)
        self.manxes = [pygame.Rect(v.x1, MANXA_Y, PAS, 6) for v in self.vagons[:-1]]
        fi = self.vagons[-1].x1
        self.paret_fi = pygame.Rect(fi + 40, -300, 20, TERRA_Y + 300)
        self._cache = {}

    def vago_a(self, x):
        """L'índex del vagó on és x (el passadís compta com el vagó de darrere)."""
        for v in self.vagons:
            if x < v.x1 + PAS:
                return v.idx
        return len(self.vagons) - 1

    def colisions(self, x):
        i = self.vago_a(x)
        c = self._cache.get(i)
        if c is None:
            solids, plats = [self.terra, self.paret_fi], []
            for j in (i - 1, i, i + 1):
                if 0 <= j < len(self.vagons):
                    solids += self.vagons[j].solids
                    plats += self.vagons[j].plats
            solids += [m for m in self.manxes if abs(m.x - x) < 1200]
            c = self._cache[i] = (solids, plats)
        portes = [self.vagons[j].porta_rect for j in (i - 1, i, i + 1)
                  if 0 <= j < len(self.vagons) and not self.vagons[j].oberta]
        if portes:
            return c[0] + portes, c[1]
        return c

    def escala_a(self, x, y):
        return self.vagons[self.vago_a(x)].escala_a(x, y)

    def al_sostre(self, cos):
        return cos.y <= SOSTRE_Y + 1


# ---------------------------------------------------------------------------------------------
# Pintar
# ---------------------------------------------------------------------------------------------
def _fosc(c, k=0.75):
    return tuple(int(v * k) for v in c)


def _clar(c, q=24):
    return tuple(min(255, v + q) for v in c)


def pintar_vago(v, atr, rng=None):
    """La superfície fixa del vagó (de DALT a VIA_Y): sostre, paret del fons amb finestres, mobles, terra."""
    rng = rng or random.Random(v.idx * 31 + 7)
    w = v.ample
    s = pygame.Surface((w, VIA_Y - DALT), pygame.SRCALPHA)
    oy = DALT
    paret, paret_f, socol, motllura = PALETES[v.tipus]

    def Y(y):
        return y - oy

    # paret del fons
    s.fill(paret, (PARET, Y(SOSTRE_INT), w - 2 * PARET, TERRA_Y - SOSTRE_INT))
    for x in range(PARET + 20, w - PARET, 40):                   # plafons
        pygame.draw.line(s, paret_f, (x, Y(SOSTRE_INT + 10)), (x, Y(TERRA_Y - 48)))
        pygame.draw.line(s, _clar(paret, 14), (x + 1, Y(SOSTRE_INT + 10)), (x + 1, Y(TERRA_Y - 48)))
    if v.tipus == "llitera":                                      # paper pintat amb rombes
        for y in range(SOSTRE_INT + 14, TERRA_Y - 50, 12):
            for x in range(PARET + 6 + (y // 12 % 2) * 6, w - PARET, 12):
                s.set_at((x, Y(y)), _clar(paret, 18))
    if v.tipus in ("equipatges", "correu"):                       # taulons
        s.fill(paret, (PARET, Y(SOSTRE_INT), w - 2 * PARET, TERRA_Y - SOSTRE_INT))
        for y in range(SOSTRE_INT + 8, TERRA_Y, 10):
            pygame.draw.line(s, paret_f, (PARET, Y(y)), (w - PARET, Y(y)))
            for x in range(PARET + rng.randint(0, 60), w - PARET, rng.randint(60, 120)):
                pygame.draw.line(s, paret_f, (x, Y(y - 9)), (x, Y(y)))
    # sòcol i motllura
    s.fill(socol, (PARET, Y(TERRA_Y - 46), w - 2 * PARET, 46))
    for x in range(PARET + 10, w - PARET, 30):
        pygame.draw.rect(s, _fosc(socol, 0.8), (x, Y(TERRA_Y - 40), 22, 32), 1)
    pygame.draw.line(s, motllura, (PARET, Y(TERRA_Y - 47)), (w - PARET, Y(TERRA_Y - 47)), 2)
    pygame.draw.line(s, _fosc(motllura, 0.6), (PARET, Y(TERRA_Y - 45)), (w - PARET, Y(TERRA_Y - 45)))
    # cornisa sota el sostre
    s.fill(_fosc(paret, 0.55), (PARET, Y(SOSTRE_INT), w - 2 * PARET, 7))
    pygame.draw.line(s, motllura, (PARET, Y(SOSTRE_INT + 7)), (w - PARET, Y(SOSTRE_INT + 7)))
    # finestres: forat transparent amb marc
    for fx, fw in v.finestres:
        x = fx - v.x0
        fy0, fy1 = (FIN_Y0, FIN_Y1) if fw >= 40 else (FIN_Y0, FIN_Y0 + 26)
        if v.tipus == "llitera":
            fy0, fy1 = 168, 204
        r = pygame.Rect(x, Y(fy0), fw, fy1 - fy0)
        pygame.draw.rect(s, (24, 12, 8), r.inflate(8, 8))
        pygame.draw.rect(s, motllura, r.inflate(6, 6), 1)
        pygame.draw.rect(s, _fosc(socol, 0.7), r.inflate(4, 4), 2)
        s.fill((0, 0, 0, 0), r)
        s.fill((80, 110, 170, 26), r)                             # reflex del vidre
        pygame.draw.line(s, (200, 220, 255, 40), (r.x + 4, r.bottom - 6), (r.x + 14, r.y + 4))
        pygame.draw.line(s, (200, 220, 255, 30), (r.x + 8, r.bottom - 4), (r.x + 18, r.y + 6))
        if fw >= 50:
            pygame.draw.line(s, (24, 12, 8), (r.x, r.centery - 6), (r.right, r.centery - 6), 2)
            for cx_, gir in ((r.x - 2, False), (r.right - 10, True)):
                img = atr.imatge("cortina", gir)
                s.blit(img, (cx_, Y(fy0 - 6)))
    # portaequipatges
    for rk in v.racks:
        x0, x1 = rk[0] - v.x0, rk[1] - v.x0
        y = rk[2] if len(rk) > 2 else RACK_Y
        if len(rk) > 2:                                           # prestatges del correu
            s.fill(_fosc(socol, 1.1), (x0, Y(y), x1 - x0, 5))
            pygame.draw.line(s, motllura, (x0, Y(y)), (x1, Y(y)))
            for bx in (x0 + 4, x1 - 6):
                pygame.draw.line(s, _fosc(socol, 0.7), (bx, Y(y + 5)), (bx + 6, Y(y + 18)), 2)
            for k in range(rng.randint(3, 8)):                    # cartes i paquets
                px = rng.randint(x0 + 4, x1 - 10)
                ph = rng.randint(4, 9)
                pygame.draw.rect(s, rng.choice([(200, 186, 150), (170, 140, 100), (220, 210, 186)]),
                                 (px, Y(y - ph), rng.randint(5, 9), ph))
            continue
        pygame.draw.line(s, (232, 196, 100), (x0, Y(y)), (x1, Y(y)), 2)
        pygame.draw.line(s, (140, 100, 36), (x0, Y(y + 2)), (x1, Y(y + 2)))
        for x in range(x0, x1, 4):
            pygame.draw.line(s, (120, 90, 40), (x, Y(y + 2)), (x + 2, Y(y + 7)))
        pygame.draw.line(s, (196, 150, 58), (x0, Y(y + 7)), (x1, Y(y + 7)))
        for bx in (x0 + 2, x1 - 2):
            pygame.draw.line(s, (196, 150, 58), (bx, Y(y)), (bx, Y(y - 10)))
            pygame.draw.line(s, (196, 150, 58), (bx, Y(y - 10)), (bx + (6 if bx < x1 - 2 else -6), Y(y - 10)))
    # llums (la peça; la llum la pinta el joc)
    for lx, ly, nom in v.llums:
        img = atr.imatge(nom)
        ax, ay = atr.anc[nom]
        s.blit(img, (lx - v.x0 - ax, Y(ly) - img.get_height() // 2 if nom == "llum" else Y(SOSTRE_INT)))
    # cartells
    from motor.dibuix import F_PETITA, render
    for cx, cy, txt in v.cartells:
        img = render(txt, F_PETITA, (238, 222, 184))
        r = img.get_rect(center=(cx - v.x0, Y(cy)))
        pygame.draw.rect(s, (30, 18, 12), r.inflate(10, 8))
        pygame.draw.rect(s, (164, 118, 56), r.inflate(10, 8), 1)
        s.blit(img, r)
    # mobles
    for nom, x, y, gir in v.mobles:
        img = atr.imatge(nom, gir)
        ax, ay = atr.anc[nom]
        if gir:
            ax = img.get_width() - ax
        s.blit(img, (round(x - v.x0 - ax), round(Y(y) - ay)))
    # escales
    for ex in v.escotilles:
        x = ex - v.x0
        for bx in (x - 7, x + 6):
            pygame.draw.line(s, (60, 62, 76), (bx, Y(SOSTRE_INT)), (bx, Y(TERRA_Y)), 2)
            pygame.draw.line(s, (120, 124, 144), (bx, Y(SOSTRE_INT)), (bx, Y(TERRA_Y)))
        for y in range(SOSTRE_INT + 6, TERRA_Y, 10):
            pygame.draw.line(s, (100, 104, 122), (x - 6, Y(y)), (x + 6, Y(y)), 2)
    # terra
    s.fill((46, 28, 20), (0, Y(TERRA_Y), w, 6))
    pygame.draw.line(s, (96, 62, 40), (0, Y(TERRA_Y)), (w, Y(TERRA_Y)))
    for x in range(rng.randint(0, 40), w, 48):
        pygame.draw.line(s, (30, 18, 12), (x, Y(TERRA_Y + 1)), (x, Y(TERRA_Y + 5)))
    # caixa de fora (granat) sota el terra
    s.fill(CAIXA_EXT, (0, Y(TERRA_Y + 6), w, CAIXA_BAIX - TERRA_Y - 6))
    pygame.draw.line(s, CAIXA_EXT_C, (0, Y(TERRA_Y + 7)), (w, Y(TERRA_Y + 7)))
    pygame.draw.line(s, (40, 10, 14), (0, Y(CAIXA_BAIX - 1)), (w, Y(CAIXA_BAIX - 1)))
    for x in range(6, w, 14):
        s.set_at((x, Y(TERRA_Y + 10)), (150, 70, 60))
    # bastidor de sota
    s.fill((24, 22, 30), (20, Y(CAIXA_BAIX), w - 40, 8))
    pygame.draw.line(s, (52, 50, 64), (20, Y(CAIXA_BAIX)), (w - 20, Y(CAIXA_BAIX)))
    for bx in (66, w - 66):                                       # bogies
        pygame.draw.rect(s, (30, 28, 38), (bx - 30, Y(CAIXA_BAIX + 6), 60, 10))
        pygame.draw.line(s, (70, 68, 84), (bx - 30, Y(CAIXA_BAIX + 6)), (bx + 30, Y(CAIXA_BAIX + 6)))
        pygame.draw.rect(s, (40, 38, 50), (bx - 6, Y(CAIXA_BAIX + 2), 12, 6))
    caixa_x = w // 2
    pygame.draw.rect(s, (30, 28, 36), (caixa_x - 26, Y(CAIXA_BAIX + 4), 52, 12))
    pygame.draw.rect(s, (56, 54, 66), (caixa_x - 26, Y(CAIXA_BAIX + 4), 52, 12), 1)
    # parets dels extrems (tall: granat amb vora clara)
    for x in (0, w - PARET):
        s.fill(CAIXA_EXT, (x, Y(SOSTRE_Y), PARET, TERRA_Y - SOSTRE_Y + 6))
        pygame.draw.line(s, CAIXA_EXT_C, (x + (PARET - 1 if x == 0 else 0), Y(SOSTRE_Y)),
                         (x + (PARET - 1 if x == 0 else 0), Y(TERRA_Y)))
        if not (v.idx == 0 and x == 0):
            s.fill((0, 0, 0, 0), (x, Y(TERRA_Y - PORTA_H), PARET, PORTA_H))       # forat de la porta
            pygame.draw.rect(s, (36, 18, 14), (x - (0 if x == 0 else 2), Y(TERRA_Y - PORTA_H - 3),
                                               PARET + 2, 3))
    if v.idx == 0:                                                # finestra del darrere
        pygame.draw.rect(s, (24, 12, 8), (0, Y(170), PARET, 60))
    # el sostre
    r = pygame.Rect(0, Y(SOSTRE_Y), w, SOSTRE_INT - SOSTRE_Y)
    pygame.draw.rect(s, SOSTRE_C, r, border_top_left_radius=6, border_top_right_radius=6)
    pygame.draw.line(s, SOSTRE_CL, (4, Y(SOSTRE_Y)), (w - 5, Y(SOSTRE_Y)))
    pygame.draw.line(s, (36, 40, 58), (0, Y(SOSTRE_INT - 3)), (w, Y(SOSTRE_INT - 3)))
    pygame.draw.line(s, (90, 98, 128), (0, Y(SOSTRE_Y + 3)), (w, Y(SOSTRE_Y + 3)))
    for x in range(10, w - 6, 16):
        s.set_at((x, Y(SOSTRE_Y + 7)), (130, 138, 170))
    for ex in v.escotilles:                                       # forats de les escotilles
        x = ex - v.x0
        s.fill((14, 12, 16), (x - 14, Y(SOSTRE_Y + 3), 28, SOSTRE_INT - SOSTRE_Y - 3))
        img = atr.imatge("escotilla")
        s.blit(img, (x - img.get_width() // 2, Y(SOSTRE_Y) - 2))
    # barana del sostre
    for x in range(30, w - 20, 64):
        pygame.draw.line(s, (40, 44, 62), (x, Y(SOSTRE_Y - 9)), (x, Y(SOSTRE_Y)))
    pygame.draw.line(s, (40, 44, 62), (30, Y(SOSTRE_Y - 9)), (w - 34, Y(SOSTRE_Y - 9)))
    pygame.draw.line(s, (74, 80, 104), (30, Y(SOSTRE_Y - 10)), (w - 34, Y(SOSTRE_Y - 10)))
    return s


def rodes(radi=11):
    """8 fotogrames d'una roda girant."""
    out = []
    for k in range(8):
        s = pygame.Surface((radi * 2 + 2, radi * 2 + 2), pygame.SRCALPHA)
        c = (radi + 1, radi + 1)
        pygame.draw.circle(s, (20, 18, 24), c, radi)
        pygame.draw.circle(s, (86, 84, 100), c, radi, 2)
        pygame.draw.circle(s, (54, 52, 64), c, radi - 3)
        for i in range(4):
            a = k * math.pi / 16 + i * math.pi / 4
            p = (c[0] + math.cos(a) * (radi - 3), c[1] + math.sin(a) * (radi - 3))
            q = (c[0] - math.cos(a) * (radi - 3), c[1] - math.sin(a) * (radi - 3))
            pygame.draw.line(s, (30, 28, 36), p, q, 2)
        pygame.draw.circle(s, (120, 118, 136), c, 3)
        out.append(s)
    return out
