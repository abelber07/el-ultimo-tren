"""El Último Tren: un roguelike en un tren nocturn que no s'atura mai.

Es juga a l'escriptori (python main.py) i al navegador (pygbag): per això el bucle és async.
Estats: intro (l'estació) → titol (el menú) → joc ⇄ pausa → estacio (entre trams) → joc → final → titol.
També: controls.
"""
import asyncio
import math
import sys

import pygame

from motor import nucli
from motor.nucli import BLANC, FPS, H, W, Pantalla

pygame.init()
PANTALLA = Pantalla()

from motor import desat  # noqa: E402
from motor.control import CONTROL  # noqa: E402
from motor.dibuix import F_GRAN, F_NEGRETA, F_PETITA, F_TEXT, Atles, text, text_contorn  # noqa: E402
from joc import dificultat  # noqa: E402
from joc.estacio import Estacio  # noqa: E402
from joc.paisatge import Paisatge  # noqa: E402
from joc.partida import Partida  # noqa: E402
from joc import interficie as ui  # noqa: E402
from joc.presentacio import FonsMenu, Intro, Logo  # noqa: E402

CONTROLS = [("A / D", "moverte"), ("ESPACIO", "saltar"), ("S", "agacharte (y agarrarte en los frenazos)"),
            ("S + ESPACIO", "bajar de una plataforma"), ("W", "subir escaleras"), ("J / clic", "golpe de paraguas"),
            ("K / clic der.", "abrir el paraguas (para golpes)"), ("MAYÚS", "voltereta"),
            ("E", "coger, lanzar y usar"), ("ESC", "pausa")]


DESC_MENU = {"jugar": "Empieza una noche nueva", "intro": "La estación de la Llanura, antes de subir",
             "controls": "Teclado, ratón y mando", "sortir": "Hasta la próxima noche"}


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
        self.ratoli = None              # posició del ratolí al llenç quan s'ha mogut
        self.ratoli_abans = None
        self.clic = None                # on s'ha fet clic aquest fotograma
        self.rects = []                 # els rectangles de les opcions dibuixades (per al ratolí)
        self.canvi_dif = 0
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
        self.clic = None
        for ev in pygame.event.get():
            if ev.type == pygame.MOUSEMOTION:
                self.ratoli = PANTALLA.a_llenc(ev.pos)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.clic = self.ratoli = PANTALLA.a_llenc(ev.pos)
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
        ops = [("jugar", "Subir al tren"), ("dif", f"Dificultad: {nom}"), ("intro", "Ver la introducción"),
               ("controls", "Controles")]
        if not nucli.WEB:
            ops.append(("sortir", "Salir"))
        return ops

    def _ratoli_menu(self):
        """El ratolí sobre una opció la tria; un clic hi accepta. Torna True si hi ha hagut clic en una opció."""
        if self.ratoli is not None and self.ratoli != self.ratoli_abans:
            self.ratoli_abans = self.ratoli
            for i, r in enumerate(self.rects):
                if r.inflate(0, 6).collidepoint(self.ratoli):
                    self.menu = i
        if self.clic is not None:
            return any(r.inflate(0, 6).collidepoint(self.clic) for r in self.rects)
        return False

    def actualitzar(self):
        self.t += 1
        c = CONTROL
        accepta = c.premut("acceptar") or c.premut("usar")
        if self.estat in ("titol", "pausa"):
            accepta = self._ratoli_menu() or accepta
        elif self.estat == "estacio" and self.estacio:
            accepta = self.estacio.ratoli(self.ratoli, self.clic) or accepta
        elif self.estat in ("controls", "final") and self.clic is not None:
            accepta = True
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
                self.canvi_dif = 12
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

    def _text_record(self):
        m = self.dades.get("millor")
        if not m:
            return None
        if m.get("fi"):
            return "Has llegado al final de esta versión"
        if m.get("tram", 1) > 1 and m.get("vago", 1) <= 1:
            return f"Mejor viaje: llegaste al tramo {m['tram']}"
        return f"Mejor viaje: tramo {m.get('tram', 1)}, vagón {m['vago']}"

    def dibuixar_titol(self, s):
        self.fons.dibuixar(s)
        baixa = max(0, 30 - self.t) * 2                 # el logotip baixa una mica en entrar
        self.logo.dibuixar(s, W // 2, 2 - baixa, self.t)
        ops = self.opcions_menu()
        pan = pygame.Rect(0, 0, 252, len(ops) * ui.PAS + 42)
        pan.midtop = (W // 2, 122)
        ui.panell(s, pan)
        self.rects = ui.llista(s, W // 2, pan.top + 11 + ui.PAS // 2, [txt for _, txt in ops], self.menu, self.t)
        clau = ops[self.menu][0]
        if clau == "dif":                               # fletxes per canviar la dificultat
            r = self.rects[self.menu]
            k = self.canvi_dif
            self.canvi_dif = max(0, k - 1)
            for costat in (-1, 1):
                x = r.centerx + 6 + costat * (r.width // 2 - 22 + (2 if k else 0))
                pygame.draw.polygon(s, ui.LLAUTO[3], [(x + costat * 4, r.centery), (x - costat, r.centery - 4),
                                                      (x - costat, r.centery + 4)])
        if clau == "dif":
            desc = dificultat.dades(self.dades["dificultat"])["desc"]
        else:
            desc = DESC_MENU[clau]
        ui.separador(s, W // 2, pan.bottom - 25, pan.width - 40)
        text(s, desc, F_PETITA, ui.SUAU, (W // 2, pan.bottom - 13))
        rec = self._text_record()
        if rec:
            text(s, rec, F_PETITA, ui.SUAU, (10, H - 8), ancora="bottomleft")
        text(s, f"v{nucli.VERSIO} · un juego de Abel", F_PETITA, ui.SUAU, (W - 10, H - 8), ancora="bottomright")
        ajuda = "W/S elegir · A/D cambiar · ENTER aceptar" if clau == "dif" else "W/S elegir · ENTER aceptar"
        ui.ajuda(s, ajuda, (W // 2, H - 10))
        if self.t < 40:
            v = pygame.Surface((W, H))
            v.set_alpha(255 - self.t * 255 // 40)
            s.blit(v, (0, 0))

    def dibuixar_controls(self, s):
        self._vel(s, 110)
        r = pygame.Rect(0, 0, 420, 262)
        r.center = (W // 2, H // 2 - 4)
        ui.panell(s, r, alfa=225)
        ui.titol_panell(s, "CONTROLES", W // 2, r.top + 18)
        for i, (k, que) in enumerate(CONTROLS):
            y = r.top + 44 + i * 17
            text(s, k, F_NEGRETA, ui.LLAUTO[3], (r.left + 132, y), ancora="midright")
            text(s, que, F_TEXT, ui.TEXT, (r.left + 148, y), ancora="midleft")
        ui.separador(s, W // 2, r.bottom - 38, r.width - 60)
        text(s, "Mando: A saltar · Y golpe · LB paraguas · B voltereta · X usar", F_PETITA, ui.SUAU,
             (W // 2, r.bottom - 26))
        ui.ajuda(s, "ENTER o ESC para volver", (W // 2, r.bottom - 12))

    def dibuixar_pausa(self, s):
        self._vel(s, 150)
        r = pygame.Rect(0, 0, 580, 250)
        r.center = (W // 2, H // 2)
        ui.panell(s, r, alfa=230)
        ui.titol_panell(s, "PAUSA", W // 2, r.top + 18)
        ops = self.opcions_pausa()
        esq = pygame.Rect(r.left + 16, r.top + 40, 184, r.height - 56)
        self.rects = ui.llista(s, esq.centerx + 6, esq.top + 22, ops, self.menu, self.t, ample=172)
        pygame.draw.line(s, (70, 54, 30), (esq.right + 12, r.top + 40), (esq.right + 12, r.bottom - 16))
        for i, (k, que) in enumerate(CONTROLS):
            y = r.top + 48 + i * 17
            text(s, k, F_PETITA, ui.LLAUTO[3], (esq.right + 100, y), ancora="midright")
            text(s, que, F_PETITA, ui.TEXT, (esq.right + 110, y), ancora="midleft")
        dif = dificultat.dades(self.partida.nom_dificultat)["nom"]
        text(s, f"Dificultad: {dif}", F_PETITA, ui.SUAU, (esq.centerx + 6, r.bottom - 16))

    def dibuixar_final(self, s):
        p = self.partida
        self._vel(s, min(170, self.t * 4))
        if self.t < 30:
            return
        j = p.jugador
        titols = {"mort": ("Te has quedado en el tren", (236, 130, 118)),
                  "alba": ("Ha salido el sol", (255, 196, 128)),
                  "tram": ("Fin del segundo tramo", ui.LLAUTO[3])}
        tit, col = titols[p.acabada]
        r = pygame.Rect(0, 0, 400, 236)
        r.center = (W // 2, H // 2)
        ui.panell(s, r, alfa=225)
        text_contorn(s, tit, F_GRAN, col, (W // 2, r.top + 28), vora=ui.FOSC)
        if p.acabada == "tram":
            sub = f"Has cruzado la {p.ruta['nom']}. De momento, el tren llega hasta aquí."
        elif p.acabada == "mort":
            sub = "Ahora eres un pasajero más."
        else:
            sub = "El tren no espera a nadie."
        text(s, sub, F_PETITA, ui.TEXT, (W // 2, r.top + 52))
        ui.separador(s, W // 2, r.top + 66, r.width - 80)
        files = [("Hora", p.esdeveniments.hora()),
                 ("Tramo", f"{p.tram} · vagón {p.vago_actual + 1} de {len(p.tren.vagons)}"),
                 ("Billetes", str(j.bitllets)), ("Pasajeros vencidos", str(p.baixes)),
                 ("Dificultad", dificultat.dades(p.nom_dificultat)["nom"])]
        for i, (k, v) in enumerate(files):
            y = r.top + 86 + i * 20
            text(s, k, F_TEXT, ui.SUAU, (W // 2 - 8, y), ancora="midright")
            text(s, v, F_NEGRETA, (255, 244, 220), (W // 2 + 8, y), ancora="midleft")
        if self.t > 60:
            ui.separador(s, W // 2, r.bottom - 28, r.width - 80)
            a = 150 + int(100 * abs(math.sin(self.t / 30)))
            text(s, "Pulsa ENTER para volver al menú", F_PETITA, (a, a, a), (W // 2, r.bottom - 14))


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
