"""Els enemics del primer tram: el passatger sense cara, la maleta viva i el polissó.

Tots són `Cos` amb `vida`, `dir`, `estat` i `t`. `compta()` diu si mantenen tancada la porta del vagó
(els adormits i les maletes que encara fan veure que són maletes, no).
"""
import math
import random

import pygame

from joc.mon import SOSTRE_Y, Cos


class Enemic(Cos):
    vida_max = 3
    nom_atles = "personatges"

    def __init__(self, x, y, vago, opcions=None):
        super().__init__(x, y)
        self.vago = vago
        self.vida = self.vida_max
        self.dir = random.choice((-1, 1))
        self.estat = "quiet"
        self.t = 0
        self.mort = False
        self.flash = 0
        self.atordit = 0
        self.anim = random.random() * 4

    def canviar(self, e):
        self.estat = e
        self.t = 0

    def compta(self):
        return not self.mort

    def despert(self):
        return True

    def despertar(self, p):
        pass

    def veu(self, j, dist=240, p=None):
        """Veu la viatgera: prou a prop (o, si ja està despert, al mateix vagó) i no al sostre."""
        if j.estat == "mort" or j.y <= SOSTRE_Y + 4 or abs(j.y - self.y) > 120:
            return False
        if p is not None and self.despert() and p.tren.vago_a(j.x) == p.tren.vago_a(self.x):
            return True
        return abs(j.x - self.x) < dist

    def rect_atac(self):
        return None

    def dany_contacte(self):
        return 0

    def rebre(self, p, dany, des_de_x, perfecte=False):
        if self.mort:
            return
        self.despertar(p)
        if self.atordit:
            dany *= 2
        self.vida -= dany
        self.flash = 6
        d = 1 if self.x >= des_de_x else -1
        self.vx = d * (3.5 if dany > 1 else 2.4)
        self.vy = -2.0
        if self.vida <= 0:
            self.morir(p)
        else:
            self.atordit = 0
            self.canviar("mal")

    def morir(self, p):
        self.mort = True
        p.mort_enemic(self)

    def actualitzar_base(self, p):
        self.t += 1
        self.anim += 0.1
        if self.flash:
            self.flash -= 1
        if self.atordit:
            self.atordit -= 1
            self.vx *= 0.85
            self.vx += p.empenta * 0.08
            self.moure(p.tren)
            return True
        if self.estat == "mal":
            self.vx *= 0.88
            self.moure(p.tren)
            if self.t > 16:
                self.canviar("persegueix")
            return True
        return False

    def atordir(self, frames=90):
        self.atordit = frames
        self.canviar("atordit")
        self.vx = -self.dir * 2.5


# ---------------------------------------------------------------------------------------------
class SenseCara(Enemic):
    ample = 14
    alt = 46
    vida_max = 3
    VEL = 0.95

    def __init__(self, x, y, vago, opcions=None):
        super().__init__(x, y, vago, opcions)
        self.dorm = bool((opcions or {}).get("dorm"))
        self.estat = "dorm" if self.dorm else "quiet"
        self.zeta = random.randint(0, 60)
        self.espera = random.randint(0, 40)

    def compta(self):
        return not self.mort and self.estat != "dorm"

    def despert(self):
        return self.estat != "dorm"

    def despertar(self, p):
        if self.estat == "dorm":
            self.canviar("desperta")
            p.text(self.x, self.y - 60, "!", (255, 220, 120))

    def rect_atac(self):
        if self.estat == "cop" and 2 <= self.t <= 9:
            x = self.x + (6 if self.dir > 0 else -34)
            return pygame.Rect(round(x), round(self.y - 40), 28, 30)
        return None

    def actualitzar(self, p):
        if self.actualitzar_base(p):
            return
        j = p.jugador
        e = self.estat
        if e == "dorm":
            self.vx = p.empenta * 0.3
            self.moure(p.tren)
            self.zeta -= 1
            if self.zeta <= 0:
                self.zeta = 70
                p.zeta(self.x + 6, self.y - 22)
            if not j.silenciós() and abs(j.x - self.x) < 52 and abs(j.y - self.y) < 70 and j.estat != "mort":
                self.despertar(p)
            return
        if e == "desperta":
            self.vx = 0
            self.moure(p.tren)
            if self.t > 36:
                self.canviar("persegueix")
            return
        if e == "quiet":
            self.vx = p.empenta * 0.5
            self.moure(p.tren)
            if self.veu(j, 220):
                self.canviar("persegueix")
                p.text(self.x, self.y - 58, "!", (255, 220, 120))
            return
        if e == "persegueix":
            if not self.veu(j, 360, p):
                self.vx = p.empenta * 0.5
                self.moure(p.tren)
                return
            dx = j.x - self.x
            self.dir = 1 if dx > 0 else -1
            if abs(dx) < 30 and abs(j.y - self.y) < 40 and self.espera <= 0:
                self.canviar("prepara")
                self.vx = 0
            else:
                self.vx = self.dir * self.VEL + p.empenta
                if self.espera > 0:
                    self.espera -= 1
                    self.vx *= 0.3
                if (j.y < self.y - 30 and abs(dx) < 50 and self.a_terra) or (self.xoc_paret and self.a_terra):
                    self.vy = -7.2
            self.anim += abs(self.vx) * 0.06
            self.moure(p.tren)
            return
        if e == "prepara":
            self.vx = p.empenta * 0.3
            self.moure(p.tren)
            if self.t >= 30:
                self.canviar("cop")
                self.vx = self.dir * 2.0
            return
        if e == "cop":
            self.vx *= 0.85
            self.moure(p.tren)
            if self.t >= 26:
                self.canviar("persegueix")
                self.espera = random.randint(30, 60)
            return
        self.canviar("persegueix")

    def fotograma(self):
        e = self.estat
        if e == "dorm":
            return "sc_dorm"
        if e == "atordit":
            return "sc_atordit"
        if e == "mal":
            return "sc_mal"
        if e == "prepara":
            return "sc_prepara"
        if e == "cop":
            return "sc_cop" if self.t < 16 else "sc_quiet"
        if e == "desperta":
            return "sc_atordit" if self.t < 18 else "sc_quiet"
        if abs(self.vx) > 0.2 and self.a_terra:
            return "sc_camina%d" % (int(self.anim * 1.6) % 4)
        return "sc_quiet"

    def dibuixar(self, surf, cam, atles):
        nom = self.fotograma()
        tremol = 0
        if self.estat == "prepara" and self.t > 18:
            tremol = (self.t % 4 < 2) * 2 - 1
        atles.dibuixar(surf, nom, self.x - cam + tremol, self.y + (2 if nom == "sc_dorm" else 0),
                       girat=self.dir < 0, blanc=self.flash > 3)
        if self.estat == "atordit" and (self.t // 6) % 2 == 0:
            for k in range(3):
                a = self.t * 0.12 + k * 2.1
                surf.fill((255, 230, 120), (round(self.x - cam + math.cos(a) * 9), round(self.y - 54 + math.sin(a) * 3),
                                            2, 2))


# ---------------------------------------------------------------------------------------------
class MaletaViva(Enemic):
    ample = 22
    alt = 13
    vida_max = 2

    def __init__(self, x, y, vago, opcions=None):
        super().__init__(x, y, vago, opcions)
        self.estat = "amagada"
        self.encallada = False
        self.salt_vx = 0.0
        self.parpelleig = random.randint(120, 300)

    def compta(self):
        return not self.mort and self.estat != "amagada"

    def despert(self):
        return self.estat != "amagada"

    def despertar(self, p):
        if self.estat == "amagada":
            self.canviar("persegueix")
            self.vy = -3.5
            p.text(self.x, self.y - 22, "!", (255, 220, 120))

    def dany_contacte(self):
        return 1 if self.estat in ("persegueix",) and not self.atordit else 0

    def actualitzar(self, p):
        if self.actualitzar_base(p):
            return
        j = p.jugador
        if self.estat == "amagada":
            self.parpelleig -= 1
            if self.parpelleig < -20:
                self.parpelleig = random.randint(150, 320)
            self.vx = p.empenta * 0.6
            self.moure(p.tren)
            if abs(j.x - self.x) < 54 and abs(j.y - self.y) < 50 and j.estat != "mort":
                self.despertar(p)
            return
        if self.estat != "persegueix":
            self.canviar("persegueix")
        if not self.a_terra:
            self.vx = self.salt_vx                   # el salt manté la direcció encara que fregui una caixa
        if self.a_terra:
            self.vx = self.vx * 0.7 + p.empenta * 0.3
            if self.t > 26 and self.veu(j, 300, p):
                self.dir = 1 if j.x > self.x else -1
                self.vx = self.salt_vx = self.dir * random.uniform(2.0, 2.8)
                self.vy = -7.8 if self.encallada else random.uniform(-5.4, -4.2)
                self.encallada = False
                self.t = random.randint(-10, 6)
        self.moure(p.tren)
        if self.xoc_paret:
            self.encallada = True

    def dibuixar(self, surf, cam, atles):
        if self.estat == "amagada":
            nom = "maleta_ulls" if self.parpelleig < 0 else "maleta"
        elif self.atordit:
            nom = "maleta"
        else:
            nom = "maleta_salt" if not self.a_terra else "maleta_obre"
        atles.dibuixar(surf, nom, self.x - cam, self.y, girat=self.dir < 0, blanc=self.flash > 3)


# ---------------------------------------------------------------------------------------------
class Polisso(Enemic):
    ample = 14
    alt = 24
    vida_max = 2

    def __init__(self, x, y, vago, opcions=None):
        super().__init__(x, y, vago, opcions)
        self.estat = "amagat"
        self.robat = 0
        self.origen = vago

    def compta(self):
        return not self.mort and self.estat not in ("amagat", "fora")

    def despertar(self, p):
        if self.estat == "amagat":
            self.canviar("persegueix")

    def actualitzar(self, p):
        if self.actualitzar_base(p):
            return
        j = p.jugador
        v = p.tren.vagons[self.origen]
        if self.estat == "amagat":
            self.vx = p.empenta * 0.5
            self.moure(p.tren)
            if self.veu(j, 170):
                self.canviar("persegueix")
                p.text(self.x, self.y - 34, "!", (255, 220, 120))
            return
        if self.estat == "persegueix":
            if not self.veu(j, 400, p):
                self.vx *= 0.8
                self.moure(p.tren)
                return
            self.dir = 1 if j.x > self.x else -1
            self.vx = self.dir * 2.9 + p.empenta
            if self.a_terra and (self.xoc_paret or (j.y < self.y - 30 and abs(j.x - self.x) < 40)):
                self.vy = -7.0
            self.anim += 0.25
            self.moure(p.tren)
            if self.rect().colliderect(j.rect()) and not j.invulnerable():
                if j.parant_cap(self.x):
                    self.atordir(80)
                    p.parada(self, perfecta=j.para_t < 12)
                    return
                if j.bitllets > 0:
                    self.robat = min(3, j.bitllets)
                    j.bitllets -= self.robat
                    j.invul = 30
                    p.text(j.x, j.y - 40, f"-{self.robat}", (255, 120, 100))
                else:
                    j.ferir(p, 1, self.x)
                self.canviar("fuig")
            return
        if self.estat == "fuig":
            self.dir = -1
            self.vx = -3.4 + p.empenta
            if self.a_terra and self.xoc_paret:
                self.vy = -7.0
            self.anim += 0.3
            self.moure(p.tren)
            if self.x < v.x0 - 20:
                self.estat = "fora"
                self.mort = True
            return
        self.canviar("persegueix")

    def morir(self, p):
        self.mort = True
        p.mort_enemic(self, extra=self.robat)

    def dibuixar(self, surf, cam, atles):
        if self.estat == "fora":
            return
        if self.estat == "amagat" or (self.estat == "persegueix" and abs(self.vx) < 0.5):
            nom = "po_quiet"
        elif self.estat == "fuig":
            nom = "po_fuig%d" % (int(self.anim) % 4)
        else:
            nom = "po_corre%d" % (int(self.anim) % 4)
        atles.dibuixar(surf, nom, self.x - cam, self.y, girat=self.dir < 0, blanc=self.flash > 3)


TIPUS = {"sense_cara": SenseCara, "maleta": MaletaViva, "polisso": Polisso}
