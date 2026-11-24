"""La viatgera: moviment, paraigua (cops, estocada i parada), tombarella, escales i llançar coses."""
import pygame

from joc.mon import SOSTRE_Y, TERRA_Y, Cos
from motor.control import CONTROL

VEL = 2.5
VEL_SIGIL = 1.0
ACC_TERRA = 0.42                # acceleració a terra (px/fotograma²) i a l'aire
ACC_AIRE = 0.3
FRE_TERRA = 0.55                # frenada sense tecles (quant es perd per fotograma)
GRAV_CIM = 0.55                 # al cim del salt, amb el botó premut, la gravetat afluixa (salts més suaus)
VEL_PARA = 0.7
SALT = -7.8
COYOTE = 6
MEMORIA_SALT = 7
VEL_VOLTA = 4.2
DURADA_VOLTA = 20
ESPERA_VOLTA = 16
VEL_ESCALA = 1.7
INVULNERABLE = 70
VIDA_INICIAL = 5

# cops: (fotogrames totals, primer actiu, últim actiu, dany, rect relatiu (dx, dy, w, h), poses)
COPS = [
    (17, 3, 8, 1, (4, -33, 32, 28), (("cop0", 3), ("cop1", 6), ("cop2", 99))),
    (17, 3, 8, 1, (4, -33, 32, 28), (("cop0", 3), ("cop1", 6), ("cop2", 99))),
    (24, 5, 11, 2, (6, -25, 40, 10), (("esto0", 5), ("esto1", 99))),
]


class Jugador(Cos):
    ample = 12
    alt = 34

    def __init__(self, x, y):
        super().__init__(x, y)
        self.dir = 1
        self.estat = "normal"         # normal, cop, para, volta, escala, mal, porta, llança, tombat, mort
        self.t = 0
        self.vida = VIDA_INICIAL
        self.vida_max = VIDA_INICIAL
        self.bitllets = 0
        self.invul = 0
        self.coyote = 0
        self.memoria_salt = 0
        self.espera_volta = 0
        self.combo = 0
        self.seguent_cop = False
        self.cop_fet = set()          # a qui ha tocat el cop d'ara
        self.para_t = 0               # fotogrames amb el paraigua obert
        self.ajupit = False
        self.porta = None             # l'objecte que porta sobre el cap
        self.anim = 0.0
        self.escala_x = None
        self.empenta = 0.0            # empenta de fora (corbes, frenades) que s'afegeix a vx
        self.frenada = False          # el tren està frenant (canvia la postura)
        self.cops_rebuts = 0
        self.morts = 0
        self.aterra = 0               # fotogrames de la postura d'aterrar
        self.gira = 0                 # fotogrames de derrapada en girar corrent
        self.pas = 0.0                # per a la pols de les passes

    # --- utilitats ---------------------------------------------------------------------------
    def rect(self):
        return super().rect(20 if self.ajupit or self.estat in ("volta", "tombat") else self.alt)

    def silenciós(self):
        return self.ajupit or self.estat == "escala"

    def invulnerable(self):
        return self.invul > 0 or (self.estat == "volta" and 2 <= self.t <= DURADA_VOLTA - 4) or self.estat == "mort"

    def rect_cop(self):
        if self.estat != "cop":
            return None
        tot, a, b, dany, (dx, dy, w, h), _ = COPS[self.combo]
        if not a <= self.t <= b:
            return None
        x = self.x + dx if self.dir > 0 else self.x - dx - w
        return pygame.Rect(round(x), round(self.y + dy), w, h)

    def dany_cop(self):
        return COPS[self.combo][3]

    def parant_cap(self, x):
        """Té el paraigua obert de cara a x."""
        return self.estat == "para" and (x - self.x) * self.dir > -4

    # --- actualitzar -------------------------------------------------------------------------
    def actualitzar(self, p):
        """p: la partida."""
        tren = p.tren
        c = CONTROL
        self.t += 1
        if self.invul:
            self.invul -= 1
        if self.espera_volta:
            self.espera_volta -= 1
        dx_in = (1 if c.aguantat("dre") else 0) - (1 if c.aguantat("esq") else 0)
        if c.premut("salt"):
            self.memoria_salt = MEMORIA_SALT
        elif self.memoria_salt:
            self.memoria_salt -= 1
        if self.a_terra:
            self.coyote = COYOTE
        elif self.coyote:
            self.coyote -= 1

        e = self.estat
        if e == "mort":
            self.vx *= 0.9
            self.moure(tren)
            return
        if e == "escala":
            self._escala(p, dx_in)
            return
        if e == "mal":
            self.vx *= 0.9
            self.moure(tren)
            if self.t > 18:
                self.canviar("porta" if self.porta else "normal")
            return
        if e == "tombat":
            self.ajupit = True
            self.vx = self.empenta
            self.moure(tren)
            if self.t > 50 and not p.esdeveniments.tunel_a(self.x):
                self.canviar("normal")
            return
        if e == "volta":
            self.vx = VEL_VOLTA * self.dir + self.empenta * 0.5
            self.ajupit = True
            self.moure(tren)
            if self.t >= DURADA_VOLTA:
                self.ajupit = False
                if not self._cap_lliure(tren):
                    self.ajupit = True
                self.canviar("normal")
                self.espera_volta = ESPERA_VOLTA
            return
        if e == "cop":
            tot = COPS[self.combo][0]
            if c.premut("cop") and self.t > 4:
                self.seguent_cop = True
            frena = 0.8 if self.a_terra else 0.96
            self.vx = self.vx * frena + self.empenta * 0.2
            if self.combo == 2 and self.t == 5:
                self.vx = 3.2 * self.dir
            self.moure(tren)
            if self.t >= tot - (5 if self.seguent_cop else 0) and self.t > 9:
                if self.seguent_cop and self.combo < 2:
                    self.començar_cop(self.combo + 1)
                elif self.t >= tot:
                    self.combo = 0
                    self.canviar("normal")
            return
        if e == "llança":
            self.vx *= 0.8
            self.moure(tren)
            if self.t > 12:
                self.canviar("normal")
            return

        # --- normal, para o porta (es pot caminar) ---
        if e == "para" and not c.aguantat("para") and self.t > 8:
            self.canviar("normal")
            e = "normal"
        self.ajupit = c.aguantat("avall") and self.a_terra and e == "normal"
        if not self.ajupit and not self._cap_lliure(tren):
            self.ajupit = True
        vel = VEL_SIGIL if self.ajupit else (VEL_PARA if e == "para" else VEL)
        if self.porta:
            vel *= 0.85
        propi = self.vx - self.empenta
        if dx_in and self.a_terra and e == "normal" and propi * dx_in < -1.6 and not self.ajupit:
            self.gira = 9                                     # derrapa abans de girar-se
            p.pols(self.x + propi * 3, self.y, 3)
        if dx_in and e != "para":
            self.dir = dx_in
        objectiu = dx_in * vel
        acc = ACC_TERRA if self.a_terra else ACC_AIRE
        if self.gira:
            acc *= 0.6
        self.vx += max(-acc, min(acc, objectiu - propi))
        if not dx_in and self.a_terra:
            self.vx = self.empenta + propi * FRE_TERRA
        # escales
        if (c.aguantat("amunt") or c.premut("amunt")) and not self.porta and e != "para":
            ex = tren.escala_a(self.x, self.y)
            if ex is not None and self.y > SOSTRE_Y + 2:
                self.començar_escala(ex)
                return
        if c.aguantat("avall") and self.a_terra and self.y <= SOSTRE_Y + 1 and not self.porta:
            ex = tren.escala_a(self.x, self.y)
            if ex is not None and self.sobre is not None:
                self.començar_escala(ex)
                self.y += 6
                return
        # saltar o baixar d'una plataforma
        if self.memoria_salt and (self.coyote or self.a_terra) and e != "para":
            if c.aguantat("avall") and self.sobre is not None:
                self.baixant = 10
                self.memoria_salt = 0
                self.y += 1
            elif self._cap_lliure(tren, 4):
                self.vy = SALT
                self.coyote = 0
                self.memoria_salt = 0
                self.ajupit = False
                p.pols(self.x, self.y, 4)
        if not c.aguantat("salt") and self.vy < -2.5 and not self.ajupit:
            self.vy *= 0.6
        # accions
        if self.porta:
            if c.premut("usar") or c.premut("cop"):
                p.llançar(self)
                self.canviar("llança")
                return
        else:
            if c.premut("cop"):
                self.començar_cop(0)
            elif c.premut("para") and e != "para":
                self.canviar("para")
                self.para_t = 0
            elif c.premut("volta") and not self.espera_volta and self.a_terra:
                self.canviar("volta")
                self.dir = dx_in or self.dir
                p.pols(self.x, self.y, 6)
            elif c.premut("usar"):
                p.usar(self)
        if self.estat == "para":
            self.para_t += 1
        vy0, terra0 = self.vy, self.a_terra
        if not self.a_terra and abs(self.vy) < 1.3 and c.aguantat("salt"):
            self.vy += GRAV_CIM - 0.36                        # moure() hi suma la gravetat normal
        self.moure(tren)
        if self.a_terra and not terra0 and vy0 > 3.2:
            self.aterra = 7 if vy0 > 6 else 4
            p.pols(self.x, self.y, 5 if vy0 > 6 else 3)
        if self.aterra:
            self.aterra -= 1
        if self.gira:
            self.gira -= 1
        if self.a_terra and dx_in:
            self.anim += abs(self.vx - self.empenta) / 15
            self.pas += abs(self.vx - self.empenta)
            if self.pas > 34 and not self.ajupit:
                self.pas = 0
                p.pols(self.x - self.dir * 4, self.y, 1)
        if self.y > TERRA_Y + 200:
            self.y = TERRA_Y
            self.vy = 0

    def _cap_lliure(self, tren, marge=0):
        """Es pot posar dret (no hi ha sostre a sobre del cap)."""
        r = pygame.Rect(round(self.x - self.ample / 2), round(self.y - self.alt - marge), self.ample, self.alt - 4)
        solids, _ = tren.colisions(self.x)
        return not any(r.colliderect(s) for s in solids)

    def començar_cop(self, n):
        self.combo = n
        self.canviar("cop")
        self.seguent_cop = False
        self.cop_fet = set()
        self.ajupit = False
        if not self.a_terra:
            self.vy = min(self.vy, 0.5)

    def començar_escala(self, ex):
        self.canviar("escala")
        self.escala_x = ex
        self.x = float(ex)
        self.vx = self.vy = 0.0
        self.ajupit = False

    def _escala(self, p, dx_in):
        c = CONTROL
        dy = (1 if c.aguantat("avall") else 0) - (1 if c.aguantat("amunt") else 0)
        self.y += dy * VEL_ESCALA
        if dy:
            self.anim += 0.08
        if self.y <= SOSTRE_Y + 0.5:                   # surt per l'escotilla al sostre
            self.y = SOSTRE_Y
            self.a_terra = True
            self.canviar("normal")
            return
        if self.y >= TERRA_Y:
            self.y = TERRA_Y
            self.canviar("normal")
            return
        if c.premut("salt") or (dx_in and self.y > TERRA_Y - 40):
            self.canviar("normal")
            self.vx = dx_in * VEL
            if c.premut("salt"):
                self.vy = SALT * 0.6

    def canviar(self, estat):
        self.estat = estat
        self.t = 0

    def ferir(self, p, dany, des_de_x, empenta=3.0):
        if self.invulnerable():
            return False
        self.vida -= dany
        self.cops_rebuts += 1
        self.invul = INVULNERABLE
        d = 1 if self.x >= des_de_x else -1
        self.vx = d * empenta
        self.vy = -3.0
        if self.porta:
            p.deixar_caure(self)
        if self.vida <= 0:
            self.vida = 0
            self.canviar("mort")
        else:
            self.canviar("mal")
        return True

    # --- dibuix ------------------------------------------------------------------------------
    def fotograma(self):
        e = self.estat
        if e == "mort":
            return "estirada"
        if e == "tombat":
            if self.t < 0:
                return "estirada"
            return "sigil%d" % (int(self.anim * 2) % 4) if abs(self.vx) > 0.3 else "ajup"
        if e == "escala":
            return "escala%d" % (int(self.anim * 2) % 2)
        if e == "mal":
            return "mal"
        if e == "volta":
            return "volta%d" % min(3, self.t * 4 // DURADA_VOLTA)
        if e == "cop":
            t = self.t
            for nom, fins in COPS[self.combo][5]:
                if t < fins:
                    return nom
                t -= fins
            return COPS[self.combo][5][-1][0]
        if e == "para":
            return "para"
        if e == "llança":
            return "llança"
        if self.porta:
            if not self.a_terra:
                return "porta0"
            return "portac%d" % (int(self.anim) % 4) if abs(self.vx - self.empenta) > 0.3 else "porta0"
        if not self.a_terra:
            if abs(self.vy) < 1.3:
                return "salt_cim"
            return "salt" if self.vy < 0 else "caiguda%d" % ((self.t // 5) % 2)
        if self.frenada and e == "normal":
            if self.ajupit:
                return "agafada"
            return ("trontolla_d%d" if self.dir > 0 else "trontolla_e%d") % ((self.t // 6) % 2)
        if self.ajupit:
            return "sigil%d" % (int(self.anim * 2) % 4) if abs(self.vx - self.empenta) > 0.3 else "ajup"
        if self.gira:
            return "gira"
        if self.aterra:
            return "aterra"
        propi = abs(self.vx - self.empenta)
        if propi > 1.6:
            return "corre%d" % (int(self.anim * 2) % 8)
        if propi > 0.4:
            return "arrenca%d" % (int(self.anim * 2) % 2)
        return "quiet%d" % ((self.t // 18) % 4)

    def dibuixar(self, surf, cam, atles):
        if self.invul and self.estat != "mort" and (self.invul // 4) % 2:
            return
        atles.dibuixar(surf, self.fotograma(), self.x - cam, self.y, girat=self.dir < 0)
