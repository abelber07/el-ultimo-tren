"""El Último Tren: un roguelike en un tren nocturn que no s'atura mai.

Es juga a l'escriptori (python main.py) i al navegador (pygbag): per això el bucle és async.
Estats: intro (l'estació) → titol (el menú) → joc ⇄ pausa → estacio (entre trams) → joc → final → titol.
També: controls.
"""
import asyncio
import sys

import pygame

from motor import nucli
from motor.nucli import AMBRE, BLANC, CREMA, FPS, H, W, Pantalla

pygame.init()
PANTALLA = Pantalla()

from motor import desat  # noqa: E402
from motor.control import CONTROL  # noqa: E402
from motor.dibuix import F_GRAN, F_NEGRETA, F_PETITA, F_TEXT, Atles, caixa, text, text_contorn  # noqa: E402
from joc import dificultat  # noqa: E402
from joc.estacio import Estacio  # noqa: E402
from joc.paisatge import Paisatge  # noqa: E402
from joc.partida import Partida  # noqa: E402
from joc.presentacio import FonsMenu, Intro, Logo, placa  # noqa: E402

CONTROLS = [("A / D", "moverte"), ("ESPACIO", "saltar"), ("S", "agacharte (y agarrarte en los frenazos)"),
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
        self.dades = desat.carregar()
        self.logo = Logo()
        self.fons = FonsMenu(self.paisatge)
        self.partida = None
        self.intro = None
        self.estacio = None
        self.t = 0
        self.menu = 0
        self.sortir = False
        self.fps = False
        if self.dades.get("intro_vista"):
            self.anar_titol()
        else:
            self.veure_intro()

    # --- canvis d'estat ------------------------------------------------------------------------
    def veure_intro(self):
        self.intro = Intro(self.paisatge, self.atles)
        self.estat = "intro"
        self.t = 0

    def anar_titol(self):
        self.estat = "titol"
        self.t = 0
        self.menu = 0
        self.intro = None

    def nova_partida(self):
        self.partida = Partida(self.atles, self.atr, paisatge=self.paisatge,
                               dificultat=self.dades["dificultat"])
        self.estat = "joc"
        CONTROL.deixar_anar()

    def desar(self):
        desat.desar(self.dades)

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

    def opcions_menu(self):
        nom = dificultat.dades(self.dades["dificultat"])["nom"]
        ops = [("jugar", "Subir al tren"), ("dif", f"Dificultad:  < {nom} >"), ("intro", "Ver la introducción"),
               ("controls", "Controles")]
        if not nucli.WEB:
            ops.append(("sortir", "Salir"))
        return ops

    def actualitzar(self):
        self.t += 1
        c = CONTROL
        accepta = c.premut("acceptar") or c.premut("usar")
        if self.estat == "intro":
            self.intro.actualitzar()
            if self.t > 20 and (accepta or c.premut("pausa") or c.premut("cop")):
                self.intro.saltar()
            if self.intro.acabada:
                self.dades["intro_vista"] = True
                self.desar()
                self.anar_titol()
            return
        if self.estat == "titol":
            self.fons.actualitzar()
            ops = self.opcions_menu()
            if c.premut("amunt"):
                self.menu = (self.menu - 1) % len(ops)
            elif c.premut("avall"):
                self.menu = (self.menu + 1) % len(ops)
            clau = ops[self.menu][0]
            if clau == "dif" and (c.premut("esq") or c.premut("dre") or accepta):
                pas = -1 if c.premut("esq") else 1
                self.dades["dificultat"] = dificultat.seguent(self.dades["dificultat"], pas)
                self.desar()
            elif accepta and self.t > 10:
                if clau == "jugar":
                    self.nova_partida()
                elif clau == "intro":
                    self.veure_intro()
                elif clau == "controls":
                    self.estat = "controls"
                elif clau == "sortir":
                    self.sortir = True
            return
        if self.estat == "controls":
            self.fons.actualitzar()
            if accepta or c.premut("pausa") or c.premut("cop"):
                self.estat = "titol"
            return
        if self.estat == "joc":
            if c.premut("pausa"):
                self.estat = "pausa"
                self.menu = 0
                return
            self.partida.actualitzar()
            p = self.partida
            if p.acabada == "tram" and p.tram == 1:
                self.estacio = Estacio(p, self.paisatge, self.atles, self.atr)
                self.estat = "estacio"
                self.t = 0
                self._guardar_record()
            elif p.acabada:
                self.estat = "final"
                self.t = 0
                self._guardar_record()
            return
        if self.estat == "estacio":
            e = self.estacio
            e.actualitzar()
            if c.premut("amunt"):
                e.moure(-1)
            elif c.premut("avall"):
                e.moure(1)
            elif accepta and e.t > 30:
                via = e.acceptar()
                if via:
                    ant = self.partida
                    self.partida = Partida(self.atles, self.atr, llavor=ant.llavor_nit, paisatge=self.paisatge,
                                           dificultat=ant.nom_dificultat, tram=ant.tram + 1, ruta=via,
                                           anterior=ant)
                    self.estacio = None
                    self.estat = "joc"
                    CONTROL.deixar_anar()
            return
        if self.estat == "pausa":
            opcions = self.opcions_pausa()
            if c.premut("pausa"):
                self.estat = "joc"
            elif c.premut("amunt"):
                self.menu = (self.menu - 1) % len(opcions)
            elif c.premut("avall"):
                self.menu = (self.menu + 1) % len(opcions)
            elif accepta:
                tria = opcions[self.menu]
                if tria == "Continuar":
                    self.estat = "joc"
                elif tria == "Empezar otra noche":
                    self.nova_partida()
                elif tria == "Volver al menú":
                    self.anar_titol()
                elif tria == "Salir":
                    self.sortir = True
            return
        if self.estat == "final":
            self.partida.paisatge.avançar(9.0)
            if self.t > 60 and accepta:
                self.anar_titol()

    def _guardar_record(self):
        p = self.partida
        fi = p.acabada == "tram"
        actual = {"tram": p.tram + (1 if fi else 0), "vago": p.vago_actual + 1, "fi": fi and p.tram >= 2,
                  "minuts": int(p.esdeveniments.minuts())}

        def clau(m):
            return (m.get("fi", False), m.get("tram", 1), m.get("vago", 0), -m.get("minuts", 999))
        m = self.dades.get("millor")
        if not m or clau(actual) > clau(m):
            self.dades["millor"] = actual
            self.desar()

    def opcions_pausa(self):
        ops = ["Continuar", "Empezar otra noche", "Volver al menú"]
        if not nucli.WEB:
            ops.append("Salir")
        return ops

    # --- dibuix ------------------------------------------------------------------------------
    def dibuixar(self):
        s = self.llenc
        if self.estat == "intro":
            self.intro.dibuixar(s)
        elif self.estat == "titol":
            self.dibuixar_titol(s)
        elif self.estat == "controls":
            self.fons.dibuixar(s)
            self.dibuixar_controls(s)
        elif self.estat == "estacio":
            self.estacio.dibuixar(s)
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
        self.fons.dibuixar(s)
        baixa = max(0, 30 - self.t) * 2                 # el logotip baixa una mica en entrar
        self.logo.dibuixar(s, W // 2, 6 - baixa, self.t)
        ops = self.opcions_menu()
        y0 = 266
        for i, (clau, txt) in enumerate(ops):
            sel = i == self.menu
            ample = 196 if sel else 180
            r = pygame.Rect(0, 0, ample, 15)
            r.center = (W // 2, y0 + i * 18)
            placa(s, r, txt, sel)
        clau = ops[self.menu][0]
        if clau == "dif":
            d = dificultat.dades(self.dades["dificultat"])
            text(s, d["desc"], F_PETITA, (210, 196, 170), (W // 2, y0 - 14))
        m = self.dades.get("millor")
        if m:
            if m.get("fi"):
                rec = "Has llegado al final de esta versión"
            elif m.get("tram", 1) > 1 and m.get("vago", 1) <= 1:
                rec = f"Mejor viaje: llegaste al tramo {m['tram']}"
            else:
                rec = f"Mejor viaje: tramo {m.get('tram', 1)}, vagón {m['vago']}"
            text(s, rec, F_PETITA, (170, 156, 130), (10, H - 8), ancora="bottomleft")
        text(s, f"v{nucli.VERSIO} · un juego de Abel", F_PETITA, (150, 140, 130), (W - 10, H - 8),
             ancora="bottomright")
        if self.t < 40:
            v = pygame.Surface((W, H))
            v.set_alpha(255 - self.t * 255 // 40)
            s.blit(v, (0, 0))

    def dibuixar_controls(self, s):
        self._vel(s, 120)
        r = pygame.Rect(W // 2 - 200, 50, 400, 260)
        caixa(s, r)
        text(s, "CONTROLES", F_GRAN, AMBRE, (W // 2, 76))
        for i, (k, que) in enumerate(CONTROLS):
            y = 108 + i * 18
            text(s, k, F_NEGRETA, AMBRE, (W // 2 - 70, y), ancora="midright")
            text(s, que, F_TEXT, CREMA, (W // 2 - 56, y), ancora="midleft")
        text(s, "Con mando: A saltar · Y golpe · LB paraguas · B voltereta · X usar", F_PETITA, (190, 180, 160),
             (W // 2, 296))
        if (self.t // 30) % 2 == 0:
            text_contorn(s, "ENTER para volver", F_PETITA, BLANC, (W // 2, 324))

    def dibuixar_pausa(self, s):
        self._vel(s, 150)
        caixa(s, pygame.Rect(W // 2 - 250, 40, 500, 280))
        text(s, "PAUSA", F_GRAN, AMBRE, (W // 2, 66))
        for i, op in enumerate(self.opcions_pausa()):
            sel = i == self.menu
            text(s, ("> " if sel else "") + op, F_NEGRETA if sel else F_TEXT, AMBRE if sel else CREMA,
                 (W // 2 - 220, 104 + i * 20), ancora="midleft")
        dif = dificultat.dades(self.partida.nom_dificultat)["nom"]
        text(s, f"Dificultad: {dif}", F_PETITA, (170, 156, 130), (W // 2 - 220, 300), ancora="midleft")
        for i, (k, que) in enumerate(CONTROLS):
            y = 104 + i * 18
            text(s, k, F_PETITA, AMBRE, (W // 2 - 10, y), ancora="midleft")
            text(s, que, F_PETITA, CREMA, (W // 2 + 80, y), ancora="midleft")

    def dibuixar_final(self, s):
        p = self.partida
        self._vel(s, min(190, self.t * 4))
        if self.t < 30:
            return
        j = p.jugador
        titols = {"mort": ("Te has quedado en el tren", (230, 120, 110)),
                  "alba": ("Ha salido el sol", (255, 190, 120)),
                  "tram": ("Fin del segundo tramo", AMBRE)}
        tit, col = titols[p.acabada]
        text_contorn(s, tit, F_GRAN, col, (W // 2, 96))
        if p.acabada == "tram":
            text(s, f"Has cruzado la {p.ruta['nom']}. Hasta aquí llega, de momento, el tren.", F_TEXT, CREMA,
                 (W // 2, 128))
        elif p.acabada == "mort":
            text(s, "Ahora eres un pasajero más.", F_TEXT, CREMA, (W // 2, 128))
        else:
            text(s, "El tren no espera a nadie.", F_TEXT, CREMA, (W // 2, 128))
        files = [("Hora", p.esdeveniments.hora()),
                 ("Tramo", f"{p.tram} · vagón {p.vago_actual + 1} de {len(p.tren.vagons)}"),
                 ("Billetes", str(j.bitllets)), ("Pasajeros vencidos", str(p.baixes)),
                 ("Dificultad", dificultat.dades(p.nom_dificultat)["nom"])]
        for i, (k, v) in enumerate(files):
            text(s, k, F_TEXT, (190, 176, 150), (W // 2 - 10, 166 + i * 20), ancora="midright")
            text(s, v, F_NEGRETA, BLANC, (W // 2 + 10, 166 + i * 20), ancora="midleft")
        if self.t > 60 and (self.t // 30) % 2 == 0:
            text_contorn(s, "Pulsa ENTER", F_NEGRETA, BLANC, (W // 2, 286))


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
