"""Una nit al tren: el tram, la viatgera, els enemics, els objectes, els esdeveniments i el HUD."""
import math
import random

import pygame

from joc import enemics, objectes
from joc.esdeveniments import Esdeveniments
from joc.jugador import Jugador
from joc.mon import PARET, PORTA_H, SOSTRE_Y, TERRA_Y, TUNEL_Y, VIA_Y
from joc.paisatge import Paisatge
from joc.tren import DALT, Tren, pintar_vago, rodes
from motor import dibuix
from motor.dibuix import F_NEGRETA, F_PETITA, F_TEXT, TextFlotant, Zeta, text, text_contorn
from motor.nucli import AMBRE, BLANC, CREMA, H, W

COLORS_BITLLET = [(240, 230, 200), (220, 60, 60), (255, 250, 230)]


def _llum_radial(r, color, maxa):
    """Halo per sumar (BLEND_RGB_ADD): negre a la vora i el color, atenuat, al mig."""
    s = pygame.Surface((r * 2, r * 2))
    s.fill((0, 0, 0))
    for k in range(r, 0, -1):
        f = maxa / 255 * (1 - k / r) ** 1.8
        pygame.draw.circle(s, tuple(int(c * f) for c in color), (r, r), k)
    return s


def _forat_llum(r, fosc):
    """Màscara per a la foscor: alfa 0 al mig i plena a la vora (es combina amb BLEND_RGBA_MIN)."""
    s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
    s.fill((*fosc, 255))
    for k in range(r, 0, -1):
        a = int(255 * (k / r) ** 1.3)
        pygame.draw.circle(s, (*fosc, a), (r, r), k)
    return s


class Partida:
    def __init__(self, atles, atrezzo, llavor=None, paisatge=None):
        self.llavor = llavor if llavor is not None else random.randrange(1 << 30)
        self.rng = random.Random(self.llavor)
        random.seed(self.llavor)              # enemics i objectes: la mateixa nit amb la mateixa llavor
        self.atles, self.atr = atles, atrezzo
        self.tren = Tren(self.llavor)
        self.paisatge = paisatge or Paisatge()
        self.esdeveniments = Esdeveniments(self.tren.llarg, self.llavor)
        v0 = self.tren.vagons[0]
        self.jugador = Jugador(v0.x0 + 70, TERRA_Y)
        self.jugador.canviar("tombat")
        self.jugador.t = -40
        self.enemics = []
        self.objectes = []
        self.projectils = []
        self.efectes = []
        for v in self.tren.vagons:
            for tipus, x, y, op in v.spawns:
                self.enemics.append(enemics.TIPUS[tipus](x, y, v.idx, op))
            for tipus, x, y in v.objectes:
                self.objectes.append(objectes.crear(tipus, x, y))
        self.cam = 0.0
        self.empenta = 0.0
        self.atur = 0
        self.tremolor = 0
        self.vago_actual = 0
        self.rotul = None              # (text, temps)
        self.missatge = None           # (text, temps)
        self.acabada = None            # "mort", "alba", "tram"
        self.t = 0
        self.baixes = 0
        self.rodes = rodes()
        self.glow = _llum_radial(52, (255, 170, 70), 110)
        self.glow_petit = _llum_radial(34, (255, 170, 70), 100)
        self.forat = _forat_llum(70, (6, 6, 14))
        self.forat_llum = _forat_llum(46, (6, 6, 14))
        self.foscor = pygame.Surface((W, H), pygame.SRCALPHA)
        self.prompt = None
        for v in self.tren.vagons:
            v.surf = pintar_vago(v, self.atr)
        self._actualitzar_portes()
        self.camera(immediata=True)
        self.mostrar_rotul(self.tren.vagons[0])

    # --- utilitats per als altres -----------------------------------------------------------
    def text(self, x, y, txt, color):
        self.efectes.append(TextFlotant(x, y, txt, color))

    def zeta(self, x, y):
        self.efectes.append(Zeta(x, y))

    def esclat(self, x, y, n, colors, **kw):
        dibuix.esclat(self.efectes, x, y, n, colors, **kw)

    def pols(self, x, y, n):
        dibuix.esclat(self.efectes, x, y - 1, n, [(110, 80, 60), (90, 66, 50)], vel=(0.4, 1.4), mida=(1, 3),
                      vida=(8, 16), grav=-0.02)

    def soroll(self, x, radi):
        for e in self.enemics:
            if not e.mort and not e.despert() and abs(e.x - x) < radi and abs(e.y - self.jugador.y) < 140:
                e.despertar(self)

    def afegir_objecte(self, tipus, x, y, vx=0.0, vy=0.0):
        o = objectes.crear(tipus, x, y)
        o.vx, o.vy = vx, vy
        o.espera = 20
        self.objectes.append(o)
        return o

    def esclat_bitllets(self, x, y, n):
        for _ in range(n):
            self.afegir_objecte("bitllet", x, y, vx=self.rng.uniform(-2.2, 2.2), vy=self.rng.uniform(-4.5, -2))

    def mort_enemic(self, e, extra=0):
        self.baixes += 1
        dibuix.fum(self.efectes, e.x, e.y - e.alt / 2, 14)
        self.esclat(e.x, e.y - e.alt / 2, 8, [(220, 220, 230), (150, 150, 170)], vel=(1, 3))
        n = {"SenseCara": 2, "MaletaViva": 1, "Polisso": 1}.get(type(e).__name__, 1) + extra
        self.esclat_bitllets(e.x, e.y - e.alt / 2, n)
        if self.rng.random() < 0.15:
            self.afegir_objecte("pa", e.x, e.y - 10, vy=-3)
        self.tremolor = max(self.tremolor, 6)
        self.soroll(e.x, 150)

    def parada(self, e, perfecta):
        if perfecta:
            self.atur = 8
            self.tremolor = 8
            self.text(e.x, e.y - e.alt - 10, "¡PARADA!", (255, 240, 170))
            self.esclat(e.x - e.dir * 8, e.y - e.alt * 0.6, 14, [(255, 255, 220), (255, 220, 120)], vel=(2, 4))
        else:
            self.esclat(e.x - e.dir * 8, e.y - e.alt * 0.6, 6, [(200, 200, 220)], vel=(1, 2))

    def usar(self, j):
        o = self._a_prop(j)
        if o is None:
            return
        if o.portable:
            self.objectes.remove(o)
            j.porta = o
            j.canviar("porta")
            j.estat = "normal"
        elif o.usable:
            o.usar(self, j)

    def _a_prop(self, j):
        millor, dmin = None, 28
        for o in self.objectes:
            if (o.portable or (o.usable and o.rètol(j))) and abs(o.y - j.y) < 30:
                d = abs(o.x - j.x)
                if d < dmin:
                    millor, dmin = o, d
        return millor

    def llançar(self, j):
        o = j.porta
        j.porta = None
        self.projectils.append(objectes.Projectil(o.tipus, j.x + j.dir * 8, j.y - 30, j.dir, o.dany))

    def deixar_caure(self, j):
        o = j.porta
        j.porta = None
        o.x, o.y = j.x, j.y - 30
        o.vx, o.vy = -j.dir * 1.5, -2
        self.objectes.append(o)

    def trencar(self, pr):
        pr.fora = True
        colors = [(146, 82, 42), (104, 54, 28), (204, 160, 62)] if pr.tipus == "maleta" else \
            [(40, 120, 70), (80, 170, 110), (170, 230, 190)]
        self.esclat(pr.x, pr.y - 6, 12, colors, vel=(1, 3.5), grav=0.2)
        self.soroll(pr.x, 170)
        if pr.tipus == "maleta" and self.rng.random() < 0.5:
            self.esclat_bitllets(pr.x, pr.y - 8, 1)

    def mostrar_rotul(self, v):
        self.rotul = (v.nom.upper(), 150)

    def missatge_curt(self, txt, temps=90):
        self.missatge = (txt, temps)

    # --- bucle -------------------------------------------------------------------------------
    def actualitzar(self):
        if self.acabada:
            return
        if self.atur:
            self.atur -= 1
            return
        self.t += 1
        es = self.esdeveniments
        es.actualitzar(self.cam)
        self.paisatge.avançar(9.0 * es.velocitat)
        self.empenta = es.empenta()
        j = self.jugador
        j.empenta = 0.0 if j.estat == "escala" else self.empenta * (0.5 if j.ajupit else 1.0)
        if j.estat == "tombat" and j.t < 0:
            j.empenta = 0.0
        j.actualitzar(self)
        self._tunel_jugador()
        for e in self.enemics:
            if not e.mort and abs(e.x - j.x) < 900:
                e.actualitzar(self)
                if e.despert():
                    e.vago = self.tren.vago_a(e.x)       # la porta la tanca qui hi és, no qui hi va néixer
                if e.xoc_paret and abs(e.xoc_paret) > 3.6 and es.frenant() and not e.mort:
                    e.rebre(self, 1, e.x - math.copysign(10, e.xoc_paret))
                    self.text(e.x, e.y - e.alt - 6, "¡PLAF!", (255, 200, 160))
        self._combat()
        for o in self.objectes:
            if abs(o.x - j.x) < 900:
                o.actualitzar(self)
        self._recollir()
        for pr in self.projectils:
            pr.actualitzar(self)
        self.projectils = [p for p in self.projectils if not p.fora]
        self.efectes = [e for e in self.efectes if not e.actualitzar()]
        self.enemics = [e for e in self.enemics if not (e.mort and getattr(e, "estat", "") == "fora")]
        self._actualitzar_portes()
        self._vago_actual()
        self.camera()
        if self.tremolor:
            self.tremolor -= 1
        if self.rotul:
            self.rotul = (self.rotul[0], self.rotul[1] - 1) if self.rotul[1] > 1 else None
        if self.missatge:
            self.missatge = (self.missatge[0], self.missatge[1] - 1) if self.missatge[1] > 1 else None
        o = self._a_prop(j) if not j.porta else None
        self.prompt = o.rètol(j) if o else None
        # final
        if j.estat == "mort" and j.t > 100:
            self.acabada = "mort"
        elif es.s_ha_fet_de_dia():
            self.acabada = "alba"
        elif j.x > self.tren.vagons[-1].x1 + 16:
            self.acabada = "tram"

    def _tunel_jugador(self):
        j = self.jugador
        es = self.esdeveniments
        if j.y <= SOSTRE_Y + 1 and es.tunel_a(j.x) and j.estat not in ("mort", "escala"):
            if j.rect().top < TUNEL_Y and j.estat != "tombat":
                if j.ferir(self, 1, j.x + 20, empenta=2):
                    j.canviar("tombat")
                    self.tremolor = 10
                    self.text(j.x, j.y - 40, "¡AY!", (255, 150, 120))
                else:
                    j.ajupit = True

    def _combat(self):
        j = self.jugador
        rc = j.rect_cop()
        rj = j.rect()
        for e in self.enemics:
            if e.mort:
                continue
            re = e.rect()
            if rc is not None and id(e) not in j.cop_fet and rc.colliderect(re):
                j.cop_fet.add(id(e))
                e.rebre(self, j.dany_cop(), j.x)
                self.atur = 3
                self.tremolor = max(self.tremolor, 3)
                self.esclat((rc.centerx + re.centerx) / 2, rc.centery, 6, [(255, 255, 255), (230, 230, 240)],
                            vel=(1, 3), vida=(6, 12))
                self.soroll(e.x, 150)
            ra = e.rect_atac()
            if ra is not None and ra.colliderect(rj):
                if j.parant_cap(e.x):
                    if e.estat == "cop" and e.t <= 9:
                        perfecta = j.para_t < 14
                        e.atordir(110 if perfecta else 50)
                        self.parada(e, perfecta)
                        j.vx = -j.dir * 1.5
                elif j.ferir(self, 1, e.x):
                    self.tremolor = 8
            dc = e.dany_contacte()
            if dc and re.colliderect(rj):
                if j.parant_cap(e.x):
                    e.atordir(70)
                    e.vx = -e.dir * 3
                    e.vy = -3
                    self.parada(e, perfecta=j.para_t < 14)
                elif j.ferir(self, dc, e.x):
                    self.tremolor = 6

    def _recollir(self):
        j = self.jugador
        rj = j.rect()
        for o in self.objectes:
            if o.recollible and not o.espera and o.rect().colliderect(rj):
                if o.tipus == "bitllet":
                    j.bitllets += 1
                    o.fora = True
                    self.esclat(o.x, o.y - 4, 5, COLORS_BITLLET, vel=(0.5, 1.5), vida=(8, 14))
                elif o.tipus == "pa" and j.vida < j.vida_max:
                    j.vida += 1
                    o.fora = True
                    self.text(j.x, j.y - 40, "+1", (140, 240, 150))
        self.objectes = [o for o in self.objectes if not o.fora]

    def _actualitzar_portes(self):
        vius = {}
        for e in self.enemics:
            if e.compta():
                vius[e.vago] = True
        for v in self.tren.vagons:
            obrir = not vius.get(v.idx)
            if obrir and not v.oberta and v.visitat:
                self.missatge_curt("Se abre la puerta", 70)
            v.oberta = obrir

    def _vago_actual(self):
        j = self.jugador
        for v in self.tren.vagons:
            if v.x0 + PARET <= j.x <= v.x1 - PARET:
                if v.idx != self.vago_actual or not v.visitat:
                    if not v.visitat:
                        v.visitat = True
                        if v.idx:
                            self.mostrar_rotul(v)
                    self.vago_actual = v.idx
                break
        v = self.tren.vagons[self.vago_actual]
        if not v.oberta and abs(j.x - (v.x1 - PARET)) < 14 and j.y > TERRA_Y - PORTA_H and not self.missatge:
            self.missatge_curt("La puerta no se abre mientras haya pasajeros despiertos", 120)

    def camera(self, immediata=False):
        j = self.jugador
        objectiu = j.x - W / 2 + j.dir * 50
        objectiu = max(-60, min(self.tren.llarg - W + 100, objectiu))
        if immediata:
            self.cam = objectiu
        else:
            self.cam += (objectiu - self.cam) * 0.08

    # --- dibuix --------------------------------------------------------------------------------
    def dibuixar(self, surf, hud=True):
        es = self.esdeveniments
        cam = round(self.cam)
        if self.tremolor:
            cam += self.rng.randint(-2, 2)
        self.paisatge.dibuixar(surf, cam, es.alba(), es.inclinacio)
        trams = []
        for e, s in es.trams_tunel():
            a, b = e - cam, s - cam
            if b > 0 and a < W:
                trams.append((a, b))
                self.paisatge.dibuixar_tunel(surf, a, b, portal_x=a, sortida_x=b)
        # vagons
        roda = self.rodes[int(self.paisatge.despl / 6) % 8]
        for i, v in enumerate(self.tren.vagons):
            x = v.x0 - cam
            if x > W or x + v.ample < 0:
                if i < len(self.tren.vagons) - 1 and v.x1 - cam < W and v.x1 + 30 - cam > 0:
                    self._manxa(surf, v.x1 - cam)
                continue
            surf.blit(v.surf, (x, DALT))
            for rx in (44, 88, v.ample - 88, v.ample - 44):
                surf.blit(roda, (x + rx - 12, VIA_Y - 23))
            if i < len(self.tren.vagons) - 1:
                self._manxa(surf, v.x1 - cam)
            # porta del davant i el llum de sobre
            px = v.x1 - PARET - cam
            if not v.oberta:
                self.atr.dibuixar(surf, "porta", px - 13, TERRA_Y)
            nom_llum = "llum_porta_g" if v.oberta else "llum_porta_v"
            self.atr.dibuixar(surf, nom_llum, px - 13, TERRA_Y - PORTA_H - 4)
            # llum dels llums de paret
            if not es.tunel_a(v.x0 + v.ample / 2):
                for lx, ly, nom in v.llums:
                    g = self.glow if nom == "llum_penjant" else self.glow_petit
                    yy = ly if nom == "llum" else ly + 10
                    surf.blit(g, (lx - cam - g.get_width() // 2, yy - g.get_height() // 2),
                              special_flags=pygame.BLEND_RGB_ADD)
        for o in self.objectes:
            if -40 < o.x - cam < W + 40:
                o.dibuixar(surf, cam, self.atr)
        for e in self.enemics:
            if not e.mort and -60 < e.x - cam < W + 60:
                e.dibuixar(surf, cam, self.atles)
        j = self.jugador
        j.dibuixar(surf, cam, self.atles)
        if j.porta:
            self.atr.dibuixar(surf, j.porta.tipus, j.x - cam, j.y - 31)
        for pr in self.projectils:
            pr.dibuixar(surf, cam, self.atr)
        for ef in self.efectes:
            ef.dibuixar(surf, cam)
        if trams:
            self._foscor(surf, trams, cam)
        if hud:
            self.dibuixar_hud(surf)

    def _manxa(self, surf, x):
        pygame.draw.rect(surf, (30, 26, 32), (x, 140, 30, TERRA_Y - 140))
        for k in range(0, 30, 5):
            pygame.draw.line(surf, (50, 44, 54), (x + k, 142), (x + k, TERRA_Y - 2))
        pygame.draw.rect(surf, (52, 56, 76), (x - 2, 140, 34, 5))
        pygame.draw.rect(surf, (44, 30, 22), (x, TERRA_Y, 30, 4))
        pygame.draw.rect(surf, (20, 18, 24), (x - 6, 308, 42, 6))
        pygame.draw.rect(surf, (60, 58, 70), (x + 8, 306, 14, 10))

    def _foscor(self, surf, trams, cam):
        f = self.foscor
        f.fill((0, 0, 0, 0))
        for a, b in trams:
            f.fill((6, 6, 14, 215), (max(0, int(a)), 0, max(0, int(min(W, b) - max(0, a))), H))
        j = self.jugador
        r = self.forat.get_width() // 2
        f.blit(self.forat, (round(j.x - cam) - r, round(j.y - 16) - r), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(f, (0, 0))

    def dibuixar_hud(self, surf):
        j = self.jugador
        es = self.esdeveniments
        # vida
        for i in range(j.vida_max):
            self.atr.dibuixar(surf, "cor" if i < j.vida else "cor_buit", 16 + i * 13, 20)
        # bitllets
        self.atr.dibuixar(surf, "bitllet", 18, 36)
        text(surf, f"x {j.bitllets}", F_TEXT, CREMA, (28, 31), ancora="midleft")
        # rellotge
        self.atr.dibuixar(surf, "rellotge", W // 2 - 26, 23)
        color = (255, 140, 110) if es.minuts() >= 300 else CREMA
        text(surf, es.hora(), F_NEGRETA, color, (W // 2 - 14, 16), ancora="midleft")
        # vagó
        v = self.tren.vagons[self.vago_actual]
        text(surf, f"TRAMO 1 · VAGÓN {v.idx + 1}/{len(self.tren.vagons)}", F_PETITA, CREMA, (W - 12, 12),
             ancora="topright")
        text(surf, v.nom, F_PETITA, (190, 170, 140), (W - 12, 24), ancora="topright")
        # avisos
        y = 52
        falta = es.avis_tunel(j.x)
        if falta is not None and (self.t // 8) % 2 == 0:
            txt = "¡TÚNEL! ¡AGÁCHATE!" if j.y <= SOSTRE_Y + 1 else "¡TÚNEL!"
            text_contorn(surf, txt, F_NEGRETA, (255, 200, 110), (W // 2, y))
            y += 16
        if es.avis_frenada() and (self.t // 6) % 2 == 0:
            text_contorn(surf, "¡FRENAZO! ¡AGÁRRATE!", F_NEGRETA, (255, 150, 120), (W // 2, y))
            y += 16
        if es.avis_corba():
            text_contorn(surf, "CURVA", F_NEGRETA, (200, 220, 255), (W // 2, y))
            y += 16
        if self.rotul:
            txt, t = self.rotul
            if t > 20 or t % 4 < 2:
                dibuix.caixa(surf, pygame.Rect(W // 2 - 110, 78, 220, 30))
                text(surf, txt, F_NEGRETA, AMBRE, (W // 2, 93))
        if self.missatge:
            text_contorn(surf, self.missatge[0], F_TEXT, BLANC, (W // 2, H - 22))
        elif self.prompt:
            text_contorn(surf, self.prompt, F_TEXT, (255, 230, 160), (W // 2, H - 22))
        elif j.estat == "tombat" and j.t < 30 and self.t < 200:
            text_contorn(surf, "Te despiertas en el último vagón...", F_TEXT, CREMA, (W // 2, H - 22))
