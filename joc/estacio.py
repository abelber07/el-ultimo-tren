"""L'estació entre tram i tram (l'Empalme del Cuervo): el tren s'atura, la viatgera baixa a l'andén i tria per
quina via continua. També hi ha la fonda, on es pot descansar a canvi de bitllets."""
import math
import random

import pygame

from joc import interficie as ui
from joc.mon import VIA_Y
from joc.rutes import RUTES, oferta
from motor.dibuix import F_NEGRETA, F_PETITA, F_TEXT, Atles, render, text
from motor.nucli import CREMA, H, W

ANDEN_Y = 318
PREU_FONDA = 3
NOM = "Empalme del Cuervo"


class Estacio:
    def __init__(self, partida, paisatge, atles_pers, atrezzo):
        self.partida = partida
        self.paisatge = paisatge
        self.pers = atles_pers
        self.atr = atrezzo
        self.ext = Atles("exterior")
        self.vies = oferta(partida.llavor_nit)
        self.sel = 1
        self.t = 0
        self.descansat = False
        self.triada = None              # la via triada (quan ja marxa)
        self.missatge = None
        self.rng = random.Random(1)
        self.vapor = []
        self.rects = []
        self.ratoli_abans = None

    def opcions(self):
        ops = [("fonda", None)]
        ops += [("via", nom) for nom in self.vies]
        return ops

    def pot_descansar(self):
        j = self.partida.jugador
        return not self.descansat and j.bitllets >= PREU_FONDA and j.vida < j.vida_max

    def ratoli(self, pos, clic):
        """El ratolí tria una targeta; el clic l'accepta."""
        if pos is not None and pos != self.ratoli_abans:
            self.ratoli_abans = pos
            for i, r in enumerate(self.rects):
                if r.collidepoint(pos):
                    self.sel = i
        return clic is not None and any(r.collidepoint(clic) for r in self.rects)

    def moure(self, pas):
        self.sel = (self.sel + pas) % len(self.opcions())

    def acceptar(self):
        """Torna el nom de la via si ja s'ha triat (llavors el joc fa el tram següent)."""
        clau, nom = self.opcions()[self.sel]
        j = self.partida.jugador
        if clau == "fonda":
            if self.pot_descansar():
                j.bitllets -= PREU_FONDA
                j.vida = min(j.vida_max, j.vida + 2)
                self.descansat = True
                self.missatge = ("Has descansado en la fonda: +2 de vida", 120)
            elif self.descansat:
                self.missatge = ("Ya has descansado esta noche", 90)
            elif j.vida >= j.vida_max:
                self.missatge = ("No te hace falta descansar", 90)
            else:
                self.missatge = (f"Hacen falta {PREU_FONDA} billetes", 90)
            return None
        r = RUTES[nom]
        if r["premi"] == "cor":
            j.vida_max += 1
            j.vida += 1
        return nom

    def actualitzar(self):
        self.t += 1
        if self.missatge:
            txt, t = self.missatge
            self.missatge = (txt, t - 1) if t > 1 else None
        if self.t % 7 == 0:
            self.vapor.append([self.rng.uniform(-10, 40), VIA_Y - 10, self.rng.uniform(0.2, 0.8),
                               self.rng.uniform(-0.6, -0.2), self.rng.uniform(6, 10), 0])
        for v in self.vapor:
            v[0] += v[2]
            v[1] += v[3]
            v[4] += 0.15
            v[5] += 1
        self.vapor = [v for v in self.vapor if v[5] < 110]

    # --- dibuix ------------------------------------------------------------------------------
    def dibuixar(self, surf):
        p = self.partida
        self.paisatge.dibuixar(surf, 0, p.esdeveniments.alba())
        pygame.draw.rect(surf, (52, 52, 66), (0, ANDEN_Y, W, VIA_Y - ANDEN_Y - 4))
        pygame.draw.rect(surf, (96, 96, 112), (0, ANDEN_Y, W, 2))
        for x in range(0, W, 24):
            pygame.draw.line(surf, (40, 40, 52), (x, ANDEN_Y + 2), (x, VIA_Y - 5))
        self.ext.dibuixar(surf, "estacio", 150, ANDEN_Y)
        text(surf, "EMPALME", F_PETITA, (232, 196, 100), (103, ANDEN_Y - 105), ombra=False)
        self.ext.dibuixar(surf, "rellotge_estacio", 196, ANDEN_Y - 88)
        self.ext.dibuixar(surf, "farola", 372, ANDEN_Y)
        self.ext.dibuixar(surf, "banc", 300, ANDEN_Y)
        # la viatgera a l'andén; el vapor del tren aturat surt per l'esquerra
        self.pers.dibuixar(surf, "quiet%d" % ((self.t // 18) % 4), 250, ANDEN_Y, girat=False)
        for x, y, vx, vy, r, t in self.vapor:
            a = int(110 * (1 - t / 110))
            s = pygame.Surface((int(r) * 2, int(r) * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 224, 236, a), (int(r), int(r)), int(r))
            surf.blit(s, (int(x - r), int(y - r)))
        self._hud(surf)
        self._panell(surf)
        if self.t < 40:
            v = pygame.Surface((W, H))
            v.set_alpha(255 - self.t * 255 // 40)
            surf.blit(v, (0, 0))

    def _hud(self, surf):
        j = self.partida.jugador
        for i in range(j.vida_max):
            self.atr.dibuixar(surf, "cor" if i < j.vida else "cor_buit", 16 + i * 13, 20)
        self.atr.dibuixar(surf, "bitllet", 18, 36)
        text(surf, f"x {j.bitllets}", F_TEXT, CREMA, (28, 31), ancora="midleft")
        self.atr.dibuixar(surf, "rellotge", W // 2 - 26, 23)
        text(surf, self.partida.esdeveniments.hora(), F_NEGRETA, CREMA, (W // 2 - 14, 16), ancora="midleft")

    def _panell(self, surf):
        r = pygame.Rect(394, 44, 236, 258)
        ui.panell(surf, r, alfa=215)
        ui.titol_panell(surf, NOM, r.centerx, r.top + 16)
        text(surf, "Fin del primer tramo. Las vías se separan.", F_PETITA, ui.SUAU, (r.centerx, r.top + 32))
        y = r.top + 44
        self.rects = []
        for i, (clau, nom) in enumerate(self.opcions()):
            sel = i == self.sel
            alt = 40 if clau == "fonda" else 58
            c = pygame.Rect(r.left + 12, y, r.width - 24, alt)
            self.rects.append(c)
            fons = pygame.Surface(c.size, pygame.SRCALPHA)
            fons.fill((*ui.GRANAT[1], 235) if sel else (255, 255, 255, 10))
            surf.blit(fons, c.topleft)
            pygame.draw.rect(surf, ui.LLAUTO[2] if sel else (70, 54, 30), c, 1)
            if sel:
                pygame.draw.line(surf, ui.LLAUTO[4], (c.left + 2, c.top), (c.right - 3, c.top))
                b = ui.bitllet()
                surf.blit(b, (c.left - b.get_width() // 2, c.top + 6 + round(math.sin(self.t / 12))))
            x = c.left + (16 if sel else 10)
            if clau == "fonda":
                apagat = not self.pot_descansar()
                col = ui.TEXT_APAGAT if apagat else ui.TEXT
                text(surf, "Descansar en la fonda", F_NEGRETA, ui.LLAUTO[3] if sel and not apagat else col,
                     (x, c.top + 12), ancora="midleft")
                text(surf, f"{PREU_FONDA} billetes: +2 de vida" + ("  (hecho)" if self.descansat else ""),
                     F_PETITA, col, (x, c.top + 28), ancora="midleft")
            else:
                ruta = RUTES[nom]
                text(surf, ruta["nom"], F_NEGRETA, ui.LLAUTO[3] if sel else ui.TEXT, (x, c.top + 12),
                     ancora="midleft")
                text(surf, ruta["desc"], F_PETITA, ui.TEXT, (x, c.top + 28), ancora="midleft")
                text(surf, ruta["premi_txt"], F_PETITA, (150, 220, 160), (x, c.top + 43), ancora="midleft")
            y += alt + 8
        ui.ajuda(surf, "W/S elegir · ENTER aceptar", (r.centerx, r.bottom - 11))
        if self.missatge:
            im = render(self.missatge[0], F_TEXT, (255, 230, 170))
            surf.blit(im, im.get_rect(center=(W // 2, H - 18)))
