"""Objectes del vagó: coses que es recullen (bitllets, pa), coses que es porten i es llancen (maletes,
ampolles), baguls que s'obren i el que ven la màquina. Tot el que es fa servir va amb E."""
import math
import random

from joc.mon import Cos

PREUS = {"venda_pa": 4, "venda_cor": 10}


class Objecte(Cos):
    ample = 10
    alt = 8
    sprite = None
    recollible = False       # es recull en tocar-lo
    portable = False         # es pot agafar amb E i llançar
    usable = False           # E fa alguna cosa (bagul, venda)

    def __init__(self, tipus, x, y):
        super().__init__(x, y)
        self.tipus = tipus
        self.sprite = tipus
        self.fora = False
        self.t = random.randint(0, 60)
        self.espera = 0          # fotogrames abans de poder-lo recollir (quan surt d'un esclat)

    def actualitzar(self, p):
        self.t += 1
        if self.espera:
            self.espera -= 1
        if not self.a_terra or abs(self.vx) > 0.05 or abs(p.empenta) > 0.05:
            self.vx = self.vx * (0.86 if self.a_terra else 0.99) + p.empenta * (0.12 if self.a_terra else 0)
            self.moure(p.tren)

    def rètol(self, j):
        return None

    def dibuixar(self, surf, cam, atr):
        dy = 0
        if self.recollible:
            dy = round(math.sin(self.t * 0.08) * 1.5) - 2
        atr.dibuixar(surf, self.sprite, self.x - cam, self.y + dy)


class Recollible(Objecte):
    recollible = True

    def __init__(self, tipus, x, y):
        super().__init__(tipus, x, y)
        self.ample, self.alt = (12, 8) if tipus == "bitllet" else (14, 9)


class Portable(Objecte):
    portable = True

    def __init__(self, tipus, x, y):
        super().__init__(tipus, x, y)
        self.ample, self.alt = (22, 13) if tipus == "maleta" else (8, 15)
        self.dany = 2 if tipus == "maleta" else 1

    def rètol(self, j):
        return "E  coger"


class Bagul(Objecte):
    usable = True
    ample, alt = 30, 22

    def __init__(self, tipus, x, y):
        super().__init__(tipus, x, y)
        self.obert = False

    def rètol(self, j):
        return None if self.obert else "E  abrir el baúl"

    def usar(self, p, j):
        if self.obert:
            return
        self.obert = True
        self.sprite = "bagul_obert"
        p.esclat_bitllets(self.x, self.y - 16, random.randint(4, 7))
        if random.random() < 0.4:
            p.afegir_objecte("pa", self.x, self.y - 20, vx=random.uniform(-1.5, 1.5), vy=-3)
        p.text(self.x, self.y - 34, "¡Billetes!", (255, 214, 120))


class Venda(Objecte):
    """Un article de la màquina expenedora, damunt d'un pedestal amb el preu."""
    usable = True
    ample, alt = 20, 30

    def __init__(self, tipus, x, y):
        super().__init__(tipus, x, y)
        self.preu = PREUS[tipus]
        self.venut = False
        self.sprite = "pa" if tipus == "venda_pa" else "cor_llauna"

    def actualitzar(self, p):
        self.t += 1

    def rètol(self, j):
        if self.venut:
            return None
        que = "pan (+2 vida)" if self.tipus == "venda_pa" else "corazón de hojalata (+1 vida máx.)"
        return f"E  comprar {que}: {self.preu} billetes"

    def usar(self, p, j):
        if self.venut:
            return
        if j.bitllets < self.preu:
            p.text(self.x, self.y - 44, "No tienes billetes suficientes", (240, 150, 130))
            return
        j.bitllets -= self.preu
        self.venut = True
        if self.tipus == "venda_pa":
            j.vida = min(j.vida_max, j.vida + 2)
            p.text(self.x, self.y - 44, "+2 vida", (140, 240, 150))
        else:
            j.vida_max += 1
            j.vida = j.vida_max
            p.text(self.x, self.y - 44, "+1 vida máxima", (140, 240, 150))
        p.esclat(self.x, self.y - 34, 14, [(255, 220, 120), (255, 255, 200)])

    def dibuixar(self, surf, cam, atr):
        import pygame
        from motor.dibuix import F_PETITA, text
        x = round(self.x - cam)
        pygame.draw.rect(surf, (40, 24, 16), (x - 9, self.y - 18, 18, 18))
        pygame.draw.rect(surf, (150, 106, 50), (x - 9, self.y - 18, 18, 18), 1)
        pygame.draw.line(surf, (200, 150, 70), (x - 10, self.y - 19), (x + 9, self.y - 19))
        if not self.venut:
            atr.dibuixar(surf, self.sprite, x, self.y - 21 + round(math.sin(self.t * 0.06) * 1.5))
            text(surf, f"{self.preu}", F_PETITA, (255, 226, 150), (x, self.y - 9))
        else:
            text(surf, "-", F_PETITA, (150, 120, 90), (x, self.y - 9))


class Projectil(Cos):
    """Una maleta o una ampolla llançada."""

    def __init__(self, tipus, x, y, dir_, dany):
        super().__init__(x, y)
        self.tipus = tipus
        self.ample, self.alt = (18, 12) if tipus == "maleta" else (8, 12)
        self.vx = 5.6 * dir_
        self.vy = -2.6
        self.dany = dany
        self.gir = 0.0
        self.fora = False
        self.dir = dir_

    def actualitzar(self, p):
        self.vy = min(8, self.vy + 0.22)
        vx0 = self.vx
        self.moure(p.tren, gravetat=False)
        self.gir += 14 * self.dir
        if self.a_terra or self.xoc_paret or abs(self.vx) < abs(vx0) * 0.5:
            p.trencar(self)
            return
        for e in p.enemics:
            if not e.mort and self.rect().colliderect(e.rect()):
                e.rebre(p, self.dany, self.x - self.dir * 10)
                p.soroll(self.x, 160)
                p.trencar(self)
                return

    def dibuixar(self, surf, cam, atr):
        import pygame
        img = pygame.transform.rotate(atr.imatge(self.tipus), self.gir % 360)
        surf.blit(img, img.get_rect(center=(round(self.x - cam), round(self.y - self.alt / 2))))


def crear(tipus, x, y):
    if tipus in ("bitllet", "pa"):
        return Recollible(tipus, x, y)
    if tipus in ("maleta", "ampolla"):
        return Portable(tipus, x, y)
    if tipus == "bagul":
        return Bagul(tipus, x, y)
    if tipus in PREUS:
        return Venda(tipus, x, y)
    raise ValueError(tipus)
