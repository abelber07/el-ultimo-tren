# El Último Tren

Un roguelike de acción en pixel art. Te despiertas en el último vagón de un tren nocturno que no para nunca y tienes que
llegar a la locomotora antes del amanecer, vagón a vagón.

**Jugar en el navegador:** https://abelber07.github.io/el-ultimo-tren/

## Cómo se juega

- Cada partida es una noche: el reloj va de las 00:00 a las 06:00 (un minuto del reloj son 5 segundos). Si sale el sol, pierdes.
- Cada vagón se genera al azar. La puerta del fondo no se abre mientras quede algún pasajero despierto dentro.
- A los que duermen puedes dejarlos atrás si pasas agachado, sin hacer ruido.
- Algunos vagones tienen una escotilla: por el techo vas más rápido, pero cuidado con los túneles.
- El tren está vivo: en las curvas todo resbala, los frenazos lo lanzan todo hacia delante (agáchate para agarrarte) y en
  los túneles se apagan las luces.
- Tres dificultades en el menú: Tranquila, Normal y Pesadilla (vida, número de pasajeros, su rapidez y lo que dura la noche).

## Controles

| Tecla | Acción |
|---|---|
| A / D (o flechas) | moverte |
| ESPACIO | saltar |
| S | agacharte (sin hacer ruido; en un frenazo, agarrarte) |
| S + ESPACIO | bajar de una plataforma |
| W | subir escaleras |
| J o clic | golpe de paraguas (tres seguidos: estocada) |
| K o clic derecho | abrir el paraguas: para golpes; justo a tiempo, aturde |
| MAYÚS | voltereta |
| E | coger, lanzar y usar |
| ESC | pausa |
| F11 / F3 | pantalla completa / FPS |

También funciona con mando (A saltar, B voltereta, X usar, Y o RB golpe, LB paraguas).

## Estado

**Versión 0.3: dos tramos, el Revisor y la primera estación.**

- Novedades de la 0.3: el Revisor, jefe del primer tramo (en su propio vagón, con segunda fase a oscuras); el
  Empalme del Cuervo, donde puedes descansar en la fonda y elegir vía (Montañas, Río con niebla o Rápida); y un
  segundo tramo según la vía elegida.

- Novedades de la 0.2: animación inicial en la estación, menú nuevo, dificultad y un frenazo que se entiende (aviso con
  cuenta atrás, la viajera se tambalea, chispas en las ruedas y flechas que marcan hacia dónde empuja).

- La viajera: correr, saltar, agacharse, voltereta, escaleras, paraguas (combo de tres golpes, parada y parada perfecta), coger y lanzar maletas y botellas.
- Vagones: furgón de cola, segunda clase, coche cama, restaurante, equipajes, correo y la máquina expendedora.
- Enemigos: el pasajero sin cara (duerme o te persigue), la maleta viva y el polizón (te roba billetes).
- Túneles (agáchate si estás en el techo), frenazos y curvas.
- Billetes, pan, baúles y la máquina (pan y corazón de hojalata).

Pendiente: el andén y los pasajeros rescatados, sonido y música, los jefes de los tramos 2-4 y la historia.

## Para desarrollar

```
py -3 -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python main.py              # jugar en el escritorio
.venv\Scripts\python -m pytest tests      # pruebas (incluye un bot que cruza el tramo)
.venv\Scripts\python tools\fer_web.py     # versión web en build_web/
```

Todo el arte es pixel art generado con código (`tools/generar_*.py`, con el pintor de `tools/pintor.py`). Si cambias un
generador, vuelve a ejecutarlo y sube los PNG/JSON de `assets/img`.

Letra: Galmuri (SIL Open Font License, ver `assets/fonts/OFL-Galmuri.txt`).
