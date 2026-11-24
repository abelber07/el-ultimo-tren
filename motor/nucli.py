"""Configuració bàsica, la finestra i l'escalat. El joc comença a main.py.

El joc es dibuixa sempre en un llenç de W x H píxels (pixel art) i després s'escala a la finestra:
a l'escriptori amb un factor enter si hi cap (nítid) i, si no, al màxim que hi cap; al navegador (pygbag)
el llenç és la mateixa pantalla i el navegador l'estira.
"""
import os
import sys

WEB = sys.platform == "emscripten"
SENSE_FINESTRA = os.environ.get("JOC_FINESTRA") == "0"          # proves i captures sense obrir finestra
if SENSE_FINESTRA:
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa: E402

W, H = 640, 360
FPS = 60
TITOL = "El Último Tren"
VERSIO = "0.4"

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ruta(*parts):
    return os.path.join(BASE, *parts)


NEGRE = (8, 8, 14)
BLANC = (250, 246, 236)
CREMA = (240, 226, 196)
AMBRE = (255, 196, 92)
VERMELL = (214, 58, 58)
GRIS = (140, 136, 150)


class Pantalla:
    def __init__(self):
        pygame.display.set_caption(TITOL)
        self.completa = False
        if WEB or SENSE_FINESTRA:
            self.finestra = pygame.display.set_mode((W, H))
            self.llenc = self.finestra if WEB else pygame.Surface((W, H))
        else:
            info = pygame.display.Info()
            k = max(1, min(3, (info.current_w - 80) // W, (info.current_h - 120) // H))
            self.finestra = pygame.display.set_mode((W * k, H * k), pygame.RESIZABLE)
            self.llenc = pygame.Surface((W, H))
        self.desti = pygame.Rect(0, 0, W, H)
        self._calcular()
        try:
            icona = pygame.image.load(ruta("assets", "img", "icona.png"))
            pygame.display.set_icon(icona)
        except (pygame.error, FileNotFoundError):
            pass

    def _calcular(self):
        fw, fh = self.finestra.get_size()
        k = min(fw / W, fh / H)
        if k >= 1:
            k = int(k) if int(k) * W <= fw and int(k) * H <= fh and k - int(k) < 0.34 else k
        w, h = int(W * k), int(H * k)
        self.desti = pygame.Rect((fw - w) // 2, (fh - h) // 2, w, h)

    def canvi_mida(self):
        if not WEB and not SENSE_FINESTRA:
            self._calcular()

    def alternar_completa(self):
        if WEB or SENSE_FINESTRA:
            return
        self.completa = not self.completa
        if self.completa:
            self.finestra = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.finestra = pygame.display.set_mode((W * 2, H * 2), pygame.RESIZABLE)
        self._calcular()

    def a_llenc(self, pos):
        """Posició de la finestra (ratolí) → posició al llenç."""
        if self.llenc is self.finestra:
            return pos
        d = self.desti
        return ((pos[0] - d.x) * W / max(1, d.w), (pos[1] - d.y) * H / max(1, d.h))

    def presentar(self):
        if self.llenc is not self.finestra and not SENSE_FINESTRA:
            self.finestra.fill((0, 0, 0))
            if self.desti.size == (W, H):
                self.finestra.blit(self.llenc, self.desti)
            elif self.desti.w % W == 0 and self.desti.h % H == 0:
                self.finestra.blit(pygame.transform.scale(self.llenc, self.desti.size), self.desti)
            else:                                                  # escala no entera: primer x2 nítid i suavitzat
                gran = pygame.transform.scale_by(self.llenc, max(1, int(self.desti.w / W)))
                self.finestra.blit(pygame.transform.smoothscale(gran, self.desti.size), self.desti)
        pygame.display.flip()
