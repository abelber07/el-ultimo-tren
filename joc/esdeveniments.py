"""El rellotge de la nit i el que li passa al tren: túnels, frenades i corbes.

Rellotge: la nit va de les 00:00 a les 06:00; un minut del rellotge són SEGONS_MINUT segons de joc.
Túnel: l'entrada recorre el tren del davant (x = llarg) cap a la cua a VEL_TUNEL px per fotograma; un punt x
és dins el túnel si entrada < x <= sortida (la sortida va LLARG_TUNEL per darrere de l'entrada).
"""
import math
import random

from motor.nucli import FPS

SEGONS_MINUT = 5
MINUTS_NIT = 6 * 60
VEL_TUNEL = 10.0
AVIS_TUNEL = 150          # fotogrames d'avís abans que la boca arribi a la viatgera
AVIS_FRENADA = 110
DURADA_FRENADA = 50


class Esdeveniments:
    def __init__(self, llarg_tren, llavor, segons_minut=SEGONS_MINUT):
        self.segons_minut = segons_minut
        self.rng = random.Random(llavor * 7 + 1)
        self.llarg = llarg_tren
        self.temps = 0
        self.proper = 32 * FPS
        self.tunels = []           # [inici, llarg]
        self.frenada = None        # fotograma en què comença l'avís
        self.corba = None          # (inici, durada, angle)
        self.inclinacio = 0.0
        self.velocitat = 1.0       # del paisatge (baixa a les frenades)
        self.historial = []

    # --- rellotge ------------------------------------------------------------------------------
    def minuts(self):
        return self.temps / (FPS * self.segons_minut)

    def hora(self):
        m = int(self.minuts())
        return f"{m // 60:02d}:{m % 60:02d}"

    def alba(self):
        """0 fins a les 05:00; 1 a les 06:00."""
        return max(0.0, min(1.0, (self.minuts() - 300) / 60))

    def s_ha_fet_de_dia(self):
        return self.minuts() >= MINUTS_NIT

    # --- túnels ------------------------------------------------------------------------------
    def _entrada(self, tun):
        return self.llarg + 40 - VEL_TUNEL * (self.temps - tun[0])

    def tunel_a(self, x):
        for tun in self.tunels:
            e = self._entrada(tun)
            if e < x <= e + tun[1]:
                return True
        return False

    def trams_tunel(self):
        """[(entrada, sortida)] en x del món dels túnels actius."""
        return [(self._entrada(t), self._entrada(t) + t[1]) for t in self.tunels]

    def avis_tunel(self, x):
        """Fotogrames que falten perquè la boca del túnel arribi a x (o None)."""
        for tun in self.tunels:
            e = self._entrada(tun)
            if 0 < e - x < VEL_TUNEL * AVIS_TUNEL:
                return (e - x) / VEL_TUNEL
        return None

    # --- frenades i corbes -------------------------------------------------------------------
    def frenant(self):
        if self.frenada is None:
            return False
        return AVIS_FRENADA <= self.temps - self.frenada < AVIS_FRENADA + DURADA_FRENADA

    def forca_frenada(self):
        """0 fora de la frenada; 1 al cop i baixant fins a 0 quan s'acaba."""
        if not self.frenant():
            return 0.0
        return 1 - (self.temps - self.frenada - AVIS_FRENADA) / DURADA_FRENADA

    def falta_frenada(self):
        """0-1: quant falta perquè comenci la frenada (1 just quan sona l'avís)."""
        if not self.avis_frenada():
            return 0.0
        return 1 - (self.temps - self.frenada) / AVIS_FRENADA

    def avis_frenada(self):
        return self.frenada is not None and self.temps - self.frenada < AVIS_FRENADA

    def empenta(self):
        """Velocitat (px/fotograma) cap a on empeny el tren tot el que no està agafat."""
        e = 0.0
        if self.frenant():
            t = self.temps - self.frenada - AVIS_FRENADA
            k = t / DURADA_FRENADA
            e += min(1.0, t / 6) * (4.2 * (1 - k) + 0.6)       # entra en 6 fotogrames i s'esvaeix
        e += math.sin(self.inclinacio) * 26
        return e

    def avis_corba(self):
        return self.corba is not None and self.temps - self.corba[0] < 40

    # --- actualitzar ---------------------------------------------------------------------------
    def actualitzar(self, cam):
        self.temps += 1
        self.tunels = [t for t in self.tunels if self._entrada(t) + t[1] > -400]
        if self.frenada is not None and self.temps - self.frenada > AVIS_FRENADA + DURADA_FRENADA + 120:
            self.frenada = None
        # velocitat del paisatge
        objectiu = 0.25 if self.frenant() else 1.0
        self.velocitat += (objectiu - self.velocitat) * (0.08 if objectiu < 1 else 0.01)
        # corba
        if self.corba:
            t0, dur, ang = self.corba
            t = self.temps - t0
            if t > dur:
                self.corba = None
                self.inclinacio = 0.0
            else:
                rampa = 60
                k = min(1.0, max(0.0, (t - 40) / rampa), max(0.0, (dur - t) / rampa))
                self.inclinacio = ang * (0.5 - 0.5 * math.cos(math.pi * k))
        if self.temps >= self.proper and not self.ocupat():
            self.llançar(self.rng.choices(["tunel", "frenada", "corba"], [0.45, 0.25, 0.3])[0])
            self.proper = self.temps + self.rng.randint(22, 38) * FPS

    def ocupat(self):
        return bool(self.tunels) or self.frenada is not None or self.corba is not None

    def llançar(self, tipus):
        self.historial.append((self.temps, tipus))
        if tipus == "tunel":
            self.tunels.append([self.temps, self.rng.randint(2800, 4800)])
        elif tipus == "frenada":
            self.frenada = self.temps
        else:
            self.corba = (self.temps, self.rng.randint(320, 460), self.rng.choice((-1, 1)) * 0.045)
