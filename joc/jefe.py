"""El Revisor: el jefe del primer tram. Espera al seu vagó (el darrer) i no deixa passar ningú sense bitllet.

Atacs:
- «Perforar»: alça la perforadora (avís llarg, els ulls brillen) i la clava a terra davant seu. Fa sortir una ona
  que corre per terra (cal saltar-la). Després es queda encallat uns moments: és quan se li pot pegar.
  Si el cop es para just a temps amb el paraigua, queda atordit.
- «¡Billete, por favor!»: des de lluny, s'ajup i s'abalança amb el braç estirat. Si t'agafa, et pren bitllets i et
  llança. Si xoca amb la paret, queda atordit. Es pot esquivar saltant o amb la voltereta.
Segona fase (meitat de vida): s'apaguen els llums del vagó, només hi ha el seu farol; va més de pressa i les ones
surten cap als dos costats.
"""
import math
import random

import pygame

from joc.enemics import TIPUS, Enemic
from joc.mon import TERRA_Y


class Ona:
    """L'ona de la perforadora: corre arran de terra."""

    def __init__(self, x, dir_, vel=3.6):
        self.x = x
        self.y = TERRA_Y
        self.dir = dir_
        self.vel = vel
        self.t = 0
        self.fora = False

    def rect(self):
        return pygame.Rect(round(self.x - 7), self.y - 12, 14, 12)

    def actualitzar(self, p):
        self.t += 1
        self.x += self.dir * self.vel
        r = self.rect()
        if self.t > 80 or any(s.colliderect(r) for s in p.tren.colisions(self.x)[0]
                              if s.height > 20 and s.top < TERRA_Y):
            self.fora = True
            p.esclat(self.x, self.y - 6, 6, [(255, 220, 120), (255, 250, 210)], vel=(1, 2.5))
        if self.t % 2 == 0:
            p.esclat(self.x, self.y - 2, 1, [(255, 210, 110), (255, 240, 190)], vel=(0.5, 1.5), vida=(8, 14),
                     grav=0.1)

    def dibuixar(self, surf, cam):
        x = round(self.x - cam)
        alt = 10 + (self.t % 6 < 3) * 2
        for k in range(3):
            c = [(255, 250, 220), (255, 214, 110), (200, 130, 40)][k]
            w = 3 - k
            pts = [(x - self.dir * (4 + k * 3), self.y), (x + self.dir * (2 - k), self.y - alt + k * 2),
                   (x + self.dir * (5 - k * 2), self.y)]
            pygame.draw.lines(surf, c, False, pts, max(1, w))


class Revisor(Enemic):
    ample = 22
    alt = 84
    vida_max = 16
    es_jefe = True
    nom = "EL REVISOR"
    VEL = 0.75

    def __init__(self, x, y, vago, opcions=None):
        super().__init__(x, y, vago, opcions)
        self.dir = -1
        self.estat = "espera"
        self.espera = 60
        self.fase = 1
        self.agafat = 0              # fotogrames que té la viatgera agafada

    # --- l'estat -------------------------------------------------------------------------------
    def despert(self):
        return self.estat != "espera"

    def actiu(self):
        return not self.mort and self.estat not in ("espera",)

    def rect_atac(self):
        if self.estat == "cop" and self.t <= 9:
            x = self.x + (4 if self.dir > 0 else -60)
            return pygame.Rect(round(x), round(self.y - 34), 56, 34)
        return None

    def rect_agafa(self):
        if self.estat == "estira" and self.t > 14:
            x = self.x + (10 if self.dir > 0 else -34)
            return pygame.Rect(round(x), round(self.y - 66), 24, 40)
        return None

    def rebre(self, p, dany, des_de_x, perfecte=False):
        """Un jefe no recula a cada cop: només fa pampallugues. Encallat o atordit, rep el doble."""
        if self.mort or self.estat in ("espera", "presenta"):
            return
        if self.estat in ("encallat", "atordit"):
            dany *= 2
        self.vida -= dany
        self.flash = 6
        p.text(self.x, self.y - self.alt - 4, str(dany), (255, 230, 200))
        if self.vida <= 0:
            self.morir(p)
        elif self.fase == 1 and self.vida <= self.vida_inicial // 2:
            self.fase = 2
            self.canviar("fase2")
            self.vx = 0
            p.fase_jefe(self)

    def atordir(self, frames=90):
        self.atordit = int(frames * 0.75)
        self.canviar("atordit")
        self.vx = -self.dir * 1.5

    def morir(self, p):
        self.mort = True
        self.flash = 0
        self.atordit = 0
        self.estat = "vençut"
        self.vx = 0
        p.jefe_vençut(self)

    # --- el cervell ---------------------------------------------------------------------------
    def actualitzar(self, p):
        if not hasattr(self, "vida_inicial"):
            self.vida_inicial = self.vida
        self.t += 1
        self.anim += 0.1
        if self.flash:
            self.flash -= 1
        j = p.jugador
        e = self.estat
        agr = self.agressio * (1.25 if self.fase == 2 else 1.0)
        if self.atordit:
            self.atordit -= 1
            self.vx *= 0.85
            self.moure(p.tren)
            if not self.atordit:
                self.canviar("camina")
                self.espera = 20
            return
        if e == "espera":
            self.vx = 0
            self.moure(p.tren)
            v = p.tren.vagons[self.vago]
            if p.tren.vago_a(j.x) == self.vago and j.x > v.x0 + 140 and j.estat != "mort":
                self.canviar("presenta")
                p.presentar_jefe(self)
            return
        if e == "presenta":
            self.vx = 0
            self.dir = 1 if j.x > self.x else -1
            self.moure(p.tren)
            if self.t == 50:
                p.text(self.x, self.y - self.alt - 10, "¡Billetes, por favor!", (255, 220, 160))
            if self.t > 120:
                self.canviar("camina")
            return
        if e == "fase2":
            self.vx = 0
            self.moure(p.tren)
            if self.t > 70:
                self.canviar("camina")
                self.espera = 10
            return
        if e == "camina":
            dx = j.x - self.x
            self.dir = 1 if dx > 0 else -1
            dist = abs(dx)
            if self.espera > 0:
                self.espera -= 1
            if self.espera <= 0 and dist < 64 and abs(j.y - self.y) < 70:
                self.canviar("alça")
                self.vx = 0
            elif self.espera <= 0 and 150 < dist < 420 and random.random() < 0.02 * agr:
                self.canviar("estira")
                self.vx = 0
            else:
                self.vx = self.dir * self.VEL * agr + p.empenta * 0.3
                self.anim += abs(self.vx) * 0.05
            self.moure(p.tren)
            return
        if e == "alça":
            self.vx = p.empenta * 0.2
            self.moure(p.tren)
            if self.t >= int(38 / agr):
                self.canviar("cop")
                self.vx = self.dir * 1.5
            return
        if e == "cop":
            self.vx *= 0.7
            self.moure(p.tren)
            if self.t == 3:
                x = self.x + self.dir * 40
                p.tremolor = max(p.tremolor, 10)
                p.esclat(x, TERRA_Y - 4, 14, [(255, 220, 120), (255, 250, 210), (180, 120, 50)], vel=(1.5, 4),
                         grav=0.2)
                p.perills.append(Ona(x, self.dir, 3.6 * min(1.3, agr)))
                if self.fase == 2:
                    p.perills.append(Ona(x, -self.dir, 3.2 * min(1.3, agr)))
            if self.t > 12:
                self.canviar("encallat")
            return
        if e == "encallat":
            self.vx = 0
            self.moure(p.tren)
            if self.t > int(70 / agr):
                self.canviar("camina")
                self.espera = int(40 / agr)
            return
        if e == "estira":
            if self.t < 22:                             # s'ajup i agafa embranzida
                self.vx = 0
            elif self.t < 80:
                self.vx = self.dir * 4.4 * min(1.2, agr)
                if self.t % 4 == 0:
                    p.pols(self.x - self.dir * 8, self.y, 2)
            else:
                self.vx *= 0.8
            self.moure(p.tren)
            if self.xoc_paret and self.t > 22:
                p.tremolor = 12
                p.text(self.x, self.y - self.alt - 6, "¡PLAF!", (255, 200, 160))
                self.atordir(120)
                return
            if self.t > 100:
                self.canviar("camina")
                self.espera = 30
            return
        if e == "agafa":
            self.vx = 0
            self.moure(p.tren)
            if self.t > 40:
                self.canviar("camina")
                self.espera = 50
            return
        self.canviar("camina")

    def agafar(self, p, j):
        """Ha atrapat la viatgera: li pren bitllets i la llança enrere."""
        self.canviar("agafa")
        robats = min(j.bitllets, 2)
        j.bitllets -= robats
        if robats:
            p.text(j.x, j.y - 50, f"-{robats} billetes", (255, 160, 140))
        else:
            p.text(j.x, j.y - 50, "¡Sin billete!", (255, 160, 140))
        j.ferir(p, 1, self.x, empenta=5)
        j.vy = -5

    # --- dibuix ------------------------------------------------------------------------------
    def fotograma(self):
        e = self.estat
        if e == "vençut":
            return "rv_vençut"
        if e == "atordit":
            return "rv_atordit%d" % ((self.t // 20) % 2)
        if e in ("presenta", "fase2"):
            return "rv_alça" if 40 < self.t < 80 else "rv_quiet%d" % ((self.t // 30) % 2)
        if e == "alça":
            return "rv_alça"
        if e == "cop":
            return "rv_cop"
        if e == "encallat":
            return "rv_encallat%d" % ((self.t // 8) % 2)
        if e == "estira":
            return "rv_cop" if self.t < 22 else "rv_estira%d" % ((self.t // 6) % 2)
        if e == "agafa":
            return "rv_estira0"
        if abs(self.vx) > 0.2:
            return "rv_camina%d" % (int(self.anim * 1.2) % 4)
        return "rv_quiet%d" % ((self.t // 40) % 2)

    def pos_farol(self):
        """On és el farol (per a la llum de la segona fase)."""
        return self.x - self.dir * 14, self.y - 40

    def dibuixar(self, surf, cam, atles):
        tremol = 0
        if self.estat == "alça" and self.t > 20:
            tremol = (self.t % 4 < 2) * 2 - 1
        atles.dibuixar(surf, self.fotograma(), self.x - cam + tremol, self.y, girat=self.dir < 0,
                       blanc=self.flash > 3)
        if self.estat == "atordit" and (self.t // 6) % 2 == 0:
            for k in range(3):
                a = self.t * 0.12 + k * 2.1
                surf.fill((255, 230, 120), (round(self.x - cam + math.cos(a) * 11),
                                            round(self.y - 92 + math.sin(a) * 3), 2, 2))


TIPUS["revisor"] = Revisor
