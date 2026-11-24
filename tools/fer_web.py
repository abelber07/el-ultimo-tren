"""Prepara la versió de navegador amb pygbag.

    python tools/fer_web.py [--servir]

Copia només el que necessita el joc (main.py, motor/, joc/, assets/) a build_web/el-ultimo-tren i hi fa
`pygbag --build` amb la plantilla de web/. El resultat queda a build_web/el-ultimo-tren/build/web
(index.html + el paquet). Amb --servir, a més, l'obre a http://localhost:8000.
"""
import os
import shutil
import subprocess
import sys

ARREL = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DESTI = os.path.join(ARREL, "build_web", "el-ultimo-tren")
COSES = ["main.py", "motor", "joc", "assets"]


def main():
    if os.path.isdir(DESTI):
        shutil.rmtree(DESTI)
    os.makedirs(DESTI)
    for c in COSES:
        o = os.path.join(ARREL, c)
        if os.path.isdir(o):
            shutil.copytree(o, os.path.join(DESTI, c), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            shutil.copy2(o, DESTI)
    ordre = [sys.executable, "-m", "pygbag", "--title", "El Último Tren", "--template",
             os.path.join(ARREL, "web", "plantilla.tmpl"), "--ume_block", "1"]
    if "--servir" not in sys.argv:
        ordre.append("--build")
    ordre.append(DESTI)
    subprocess.run(ordre, check=True, cwd=os.path.dirname(DESTI))
    print("web feta a", os.path.join(DESTI, "build", "web"))


if __name__ == "__main__":
    main()
