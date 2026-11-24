# El Último Tren

Roguelike de Abel (abelber07) en Python + pygame-ce, jugable en el navegador con pygbag (GitHub Pages) y en el escritorio.
No tiene nada que ver con NEXUS (otro juego suyo): de allí solo viene el pintor de pixel art (`tools/pintor.py`) y la letra.

## Convenciones

- Código, comentarios, identificadores y workflows en catalán; commits y README en castellano.
- Textos visibles del juego en castellano.
- Todo el arte es pixel art generado con código (`tools/generar_*.py` → `assets/img/*.png` + `.json`). Nada de imágenes externas.
- Todo lo que se usa va con la acción `usar` (E / cuadrado); abajo solo agacha o baja de plataformas.
- 60 FPS fijos, lienzo de 640x360 (`motor/nucli.py`). El bucle de `main.py` es async (pygbag).

## Estructura

| Carpeta | Qué hay |
|---|---|
| `main.py` | `Joc`: estados (intro, menú, controles, juego, pausa, final) y el bucle |
| `motor/` | `nucli` (ventana y escalado), `control` (teclado/ratón/mando → acciones), `dibuix` (letras, `Atles`, partículas), `desat` (opciones y récord: JSON o localStorage; `JOC_DADES` para pruebas) |
| `joc/mon.py` | medidas del tren (SOSTRE_Y, TERRA_Y...) y `Cos` (física con sólidos y plataformas de un sentido) |
| `joc/tren.py` | `Tren` y `Vago`: generación de cada tipo de vagón (`GENERADORS`), colisiones y `pintar_vago` |
| `joc/partida.py` | `Partida`: una noche (jugador, enemigos, objetos, puertas, cámara, túneles y HUD) |
| `joc/jugador.py`, `joc/enemics.py`, `joc/objectes.py` | la viajera, los enemigos (`TIPUS`) y los objetos |
| `joc/esdeveniments.py` | reloj de la noche, túneles, frenazos y curvas |
| `joc/paisatge.py` | cielo, capas de parallax y túnel |
| `joc/dificultat.py` | los tres niveles (`DIFICULTATS`) |
| `joc/jefe.py` | el Revisor (jefe del tramo 1) y su onda |
| `joc/rutes.py`, `joc/estacio.py` | las vías que se eligen entre tramos y la estación (fonda + elección) |
| `joc/exterior.py`, `joc/presentacio.py` | el tren visto de fuera; logo, menú y la animación inicial (`Intro`) |
| `tools/` | generadores de arte, `captures.py` (capturas sin ventana), `fer_web.py` (build de pygbag) |
| `tests/` | pruebas con `JOC_FINESTRA=0`, incluido un bot que cruza el tramo entero |

Antes de dar algo visual por bueno: `python tools/captures.py <carpeta>` y mirar las capturas.
