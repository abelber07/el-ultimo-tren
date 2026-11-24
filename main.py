"""El Último Tren: un roguelike en un tren nocturn que no s'atura mai.

Es juga a l'escriptori (python main.py) i al navegador (pygbag): per això el bucle és async.
"""
import asyncio
import sys

import pygame

from motor import nucli
from motor.nucli import AMBRE, BLANC, CREMA, FPS, H, W, Pantalla

pygame.init()
PANTALLA = Pantalla()

from motor.control import CONTROL  # noqa: E402
from motor.dibuix import F_GRAN, F_NEGRETA, F_PETITA, F_TEXT, F_TITOL, Atles, caixa, text, text_contorn  # noqa: E402
from joc.paisatge import Paisatge  # noqa: E402
from joc.partida import Partida  # noqa: E402

CONTROLS = [("A / D", "moverte"), ("ESPACIO", "saltar"), ("S", "agacharte (sin hacer ruido)"),
            ("S + ESPACIO", "bajar de una plataforma"), ("W", "subir escaleras"), ("J / clic", "golpe de paraguas"),
            ("K / clic der.", "abrir el paraguas (para golpes)"), ("MAYÚS", "voltereta"),
            ("E", "coger, lanzar y usar"), ("ESC", "pausa")]


class Joc:
    def __init__(self):
        self.llenc = PANTALLA.llenc
        self.rellotge = pygame.time.Clock()
        self.atles = Atles("personatges")
        self.atr = Atles("atrezzo")
        self.atr.afegir(self.atles, ["maleta"])
        self.paisatge = Paisatge()
        self.estat = "titol"
        self.t = 0
        self.partida = Partida(self.atles, self.atr, llavor=1, paisatge=self.paisatge)
        self.menu = 0
        self.sortir = False
        self.fps = False

    def nova_partida(self):
        self.partida = Partida(self.atles, self.atr, paisatge=self.paisatge)
        self.estat = "joc"
        CONTROL.deixar_anar()

    # --- esdeveniments -------------------------------------------------------------------------
    def gestionar(self):
        CONTROL.començar()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.sortir = True
            elif ev.type == pygame.VIDEORESIZE:
                PANTALLA.canvi_mida()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F11:
                PANTALLA.alternar_completa()
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_F3:
                self.fps = not self.fps
            elif ev.type == pygame.WINDOWFOCUSLOST:
                CONTROL.deixar_anar()
                if self.estat == "joc":
                    self.estat = "pausa"
                    self.menu = 0
            CONTROL.event(ev)

    def actualitzar(self):
        self.t += 1
        c = CONTROL
        if self.estat == "titol":
            self.partida.paisatge.avançar(9.0)
            if c.premut("acceptar") or c.premut("cop") or c.premut("usar"):
                self.nova_partida()
            return
        if self.estat == "joc":
            if c.premut("pausa"):
                self.estat = "pausa"
                self.menu = 0
                return
            self.partida.actualitzar()
            if self.partida.acabada:
                self.estat = "final"
                self.t = 0
            return
        if self.estat == "pausa":
            opcions = self.opcions_pausa()
            if c.premut("pausa"):
                self.estat = "joc"
            elif c.premut("amunt"):
                self.menu = (self.menu - 1) % len(opcions)
            elif c.premut("avall"):
                self.menu = (self.menu + 1) % len(opcions)
            elif c.premut("acceptar") or c.premut("usar"):
                tria = opcions[self.menu]
                if tria == "Continuar":
                    self.estat = "joc"
                elif tria == "Empezar otra noche":
                    self.nova_partida()
                elif tria == "Volver al título":
                    self.estat = "titol"
                elif tria == "Salir":
                    self.sortir = True
            return
        if self.estat == "final":
            self.partida.paisatge.avançar(9.0)
            if self.t > 60 and (c.premut("acceptar") or c.premut("usar")):
                self.estat = "titol"
                self.partida = Partida(self.atles, self.atr, llavor=1, paisatge=self.paisatge)

    def opcions_pausa(self):
        ops = ["Continuar", "Empezar otra noche", "Volver al título"]
        if not nucli.WEB:
            ops.append("Salir")
        return ops

    # --- dibuix ------------------------------------------------------------------------------
    def dibuixar(self):
        s = self.llenc
        if self.estat == "titol":
            self.dibuixar_titol(s)
        elif self.estat in ("joc", "pausa"):
            self.partida.dibuixar(s)
            if self.estat == "pausa":
                self.dibuixar_pausa(s)
        elif self.estat == "final":
            self.partida.dibuixar(s, hud=False)
            self.dibuixar_final(s)
        if self.fps:
            text(s, f"{self.rellotge.get_fps():.0f} FPS", F_PETITA, BLANC, (W - 8, H - 8), ancora="bottomright")
        PANTALLA.presentar()

    def _vel(self, s, alfa):
        v = pygame.Surface((W, H), pygame.SRCALPHA)
        v.fill((6, 6, 14, alfa))
        s.blit(v, (0, 0))

    def dibuixar_titol(self, s):
        p = self.partida
        p.cam = 700 + (self.t * 0.2) % 400
        p.dibuixar(s, hud=False)
        self._vel(s, 165)
        text_contorn(s, "EL ÚLTIMO TREN", F_TITOL, AMBRE, (W // 2, 120))
        text(s, "un tren que solo pasa de noche", F_TEXT, CREMA, (W // 2, 152))
        if (self.t // 30) % 2 == 0:
            text_contorn(s, "Pulsa ENTER para subir", F_NEGRETA, BLANC, (W // 2, 214))
        text(s, "Llega a la locomotora antes del amanecer.", F_PETITA, (190, 180, 160), (W // 2, 250))
        text(s, f"versión {nucli.VERSIO} · un juego de Abel", F_PETITA, (150, 140, 130), (W // 2, H - 14))

    def dibuixar_pausa(self, s):
        self._vel(s, 150)
        caixa(s, pygame.Rect(W // 2 - 250, 40, 500, 280))
        text(s, "PAUSA", F_GRAN, AMBRE, (W // 2, 66))
        for i, op in enumerate(self.opcions_pausa()):
            sel = i == self.menu
            text(s, ("> " if sel else "") + op, F_NEGRETA if sel else F_TEXT, AMBRE if sel else CREMA,
                 (W // 2 - 220, 104 + i * 20), ancora="midleft")
        for i, (k, que) in enumerate(CONTROLS):
            y = 104 + i * 18
            text(s, k, F_PETITA, AMBRE, (W // 2 - 10, y), ancora="midleft")
            text(s, que, F_PETITA, CREMA, (W // 2 + 86, y), ancora="midleft")

    def dibuixar_final(self, s):
        p = self.partida
        self._vel(s, min(190, self.t * 4))
        if self.t < 30:
            return
        j = p.jugador
        titols = {"mort": ("Te has quedado en el tren", (230, 120, 110)),
                  "alba": ("Ha salido el sol", (255, 190, 120)),
                  "tram": ("Estación de la Llanura", AMBRE)}
        tit, col = titols[p.acabada]
        text_contorn(s, tit, F_GRAN, col, (W // 2, 96))
        if p.acabada == "tram":
            text(s, "Has cruzado el primer tramo. Aquí acaba, de momento, esta versión.", F_TEXT, CREMA,
                 (W // 2, 128))
        elif p.acabada == "mort":
            text(s, "Ahora eres un pasajero más.", F_TEXT, CREMA, (W // 2, 128))
        else:
            text(s, "El tren no espera a nadie.", F_TEXT, CREMA, (W // 2, 128))
        files = [("Hora", p.esdeveniments.hora()), ("Vagones", f"{p.vago_actual + 1} de {len(p.tren.vagons)}"),
                 ("Billetes", str(j.bitllets)), ("Pasajeros vencidos", str(p.baixes))]
        for i, (k, v) in enumerate(files):
            text(s, k, F_TEXT, (190, 176, 150), (W // 2 - 10, 170 + i * 20), ancora="midright")
            text(s, v, F_NEGRETA, BLANC, (W // 2 + 10, 170 + i * 20), ancora="midleft")
        if self.t > 60 and (self.t // 30) % 2 == 0:
            text_contorn(s, "Pulsa ENTER", F_NEGRETA, BLANC, (W // 2, 280))


async def main():
    joc = Joc()
    while not joc.sortir:
        joc.gestionar()
        joc.actualitzar()
        joc.dibuixar()
        joc.rellotge.tick(FPS)
        await asyncio.sleep(0)
    pygame.quit()
    if not nucli.WEB:
        sys.exit()


if __name__ == "__main__":
    asyncio.run(main())
