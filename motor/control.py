"""Teclat, ratolí i comandament → accions del joc.

Cada fotograma: `CONTROL.començar()`, després `CONTROL.event(ev)` per a cada esdeveniment, i el joc pregunta
`CONTROL.premut("cop")` (s'ha premut aquest fotograma) o `CONTROL.aguantat("esq")` (s'està aguantant).
Tot el que es fa servir (coses, màquines, baguls) va amb l'acció `usar` (E o quadrat).
"""
import pygame

TECLES = {
    "esq": (pygame.K_a, pygame.K_LEFT),
    "dre": (pygame.K_d, pygame.K_RIGHT),
    "amunt": (pygame.K_w, pygame.K_UP),
    "avall": (pygame.K_s, pygame.K_DOWN),
    "salt": (pygame.K_SPACE,),
    "cop": (pygame.K_j, pygame.K_z),
    "para": (pygame.K_k, pygame.K_x),
    "volta": (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_l),
    "usar": (pygame.K_e,),
    "acceptar": (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE),
    "pausa": (pygame.K_ESCAPE, pygame.K_p),
}
# comandament (disposició Xbox; a PlayStation: A=creu, B=cercle, X=quadrat, Y=triangle)
BOTONS = {0: ("salt", "acceptar"), 1: ("volta",), 2: ("usar",), 3: ("cop",), 4: ("para",), 5: ("cop",),
          7: ("pausa",), 6: ("pausa",)}
RATOLI = {1: ("cop",), 3: ("para",)}


class Control:
    def __init__(self):
        self.ara = set()
        self.aguant = set()
        self.eix = {"esq": False, "dre": False, "amunt": False, "avall": False}
        self.mandos = []
        self.ultim = "teclat"
        self.qualsevol = False

    def començar(self):
        self.ara = set()
        self.qualsevol = False

    def _baixa(self, accions):
        for a in accions:
            self.ara.add(a)
            self.aguant.add(a)
        self.qualsevol = True

    def _puja(self, accions):
        for a in accions:
            self.aguant.discard(a)

    def event(self, ev):
        if ev.type == pygame.KEYDOWN:
            self.ultim = "teclat"
            self._baixa([a for a, ks in TECLES.items() if ev.key in ks])
            self.qualsevol = True
        elif ev.type == pygame.KEYUP:
            self._puja([a for a, ks in TECLES.items() if ev.key in ks])
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            self._baixa(RATOLI.get(ev.button, ()))
        elif ev.type == pygame.MOUSEBUTTONUP:
            self._puja(RATOLI.get(ev.button, ()))
        elif ev.type == pygame.JOYBUTTONDOWN:
            self.ultim = "mando"
            self._baixa(BOTONS.get(ev.button, ()))
        elif ev.type == pygame.JOYBUTTONUP:
            self._puja(BOTONS.get(ev.button, ()))
        elif ev.type == pygame.JOYDEVICEADDED:
            try:
                self.mandos.append(pygame.joystick.Joystick(ev.device_index))
            except pygame.error:
                pass
        elif ev.type == pygame.JOYAXISMOTION and ev.axis in (0, 1):
            self.ultim = "mando"
            neg, pos = ("esq", "dre") if ev.axis == 0 else ("amunt", "avall")
            for nom, actiu in ((neg, ev.value < -0.5), (pos, ev.value > 0.5)):
                if actiu and not self.eix[nom]:
                    self._baixa([nom])
                elif not actiu and self.eix[nom]:
                    self._puja([nom])
                self.eix[nom] = actiu
        elif ev.type == pygame.JOYHATMOTION:
            hx, hy = ev.value
            for nom, actiu in (("esq", hx < 0), ("dre", hx > 0), ("amunt", hy > 0), ("avall", hy < 0)):
                if actiu and not self.eix[nom]:
                    self._baixa([nom])
                elif not actiu and self.eix[nom]:
                    self._puja([nom])
                self.eix[nom] = actiu

    def premut(self, accio):
        return accio in self.ara

    def aguantat(self, accio):
        return accio in self.aguant

    def deixar_anar(self):
        self.aguant.clear()
        self.ara.clear()


CONTROL = Control()
