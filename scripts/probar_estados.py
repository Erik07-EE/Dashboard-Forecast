# -*- coding: utf-8 -*-
"""Compara los 6 estados calculados en Python contra los del dashboard.

⚠️ POR QUE EXISTE: la regla que reparte los codigos en Quiebre / Riesgo / Ideal /
Exceso / Sin rotacion / Lanzamientos esta escrita DOS VECES:

  - `stkCalc` en scripts/plantilla.html  -> la que se ve en pantalla
  - `estado_de` en scripts/generar_dashboard.py -> la que congela la foto mensual

No hay forma de evitarlo: la foto hay que calcularla antes de generar el HTML. Esta
prueba es el seguro. **Correrla despues de tocar cualquier cosa de los estados** (el
maximo, el minimo, la ventana de sin rotacion, el orden de evaluacion...).

Compara codigo por codigo sobre el Dashboard_Forecast.html generado y falla si hay una
sola diferencia, diciendo cual.

Se corre con:  python scripts/probar_estados.py
"""
import io
import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import generar_dashboard as G

HTML = os.path.join(BASE, "Dashboard_Forecast.html")
if not os.path.exists(HTML):
    sys.exit("No esta %s: hay que generar el dashboard antes de correr la prueba." % HTML)

s = io.open(HTML, encoding="utf-8").read()
i = s.index("const DATA =") + len("const DATA =")
D = json.loads(s[i:s.index("\n", i)].rstrip().rstrip(";"))

# --- la misma regla, pero copiada de la PLANTILLA (stkCalc), no de generar_dashboard.
# Se transcribe aca a proposito: si alguien cambia una sola de las dos, esto lo cantа.
VRM = 6


def como_en_pantalla(r):
    cat = D["CAT"][r[3]]
    if cat in ("N", "P"): return "lanz"
    stock = r[4] or 0
    if stock <= 0: return "cero"
    maxU = r[108] or 0
    idd = r[78] or 0
    imp = (D["UN"][r[0]] == "Importados")
    minU = maxU * (max(0.0, (idd - 1) / idd) if (imp and idd) else 0.5)
    a = (D.get("hist") or {}).get("real", {}).get(r[2])
    vendio6 = bool(a) and sum(x or 0 for x in a[-VRM:]) > 0
    movio = max(r[109] or 0, max(0, (r[6] or 0) - stock)) > 0
    if not vendio6 and not movio: return "sinrot"
    if stock < minU: return "riesgo"
    if stock > maxU: return "exceso"
    return "ideal"


difs = []
cuenta = {}
for r in D["rows"]:
    a = G.estado_de(r, D)
    b = como_en_pantalla(r)
    cuenta[a] = cuenta.get(a, 0) + 1
    if a != b:
        difs.append((r[2], D["GA"][r[1]], "generador=%s" % a, "pantalla=%s" % b))

print("Codigos comparados:", len(D["rows"]))
print("Reparto:", " ".join("%s %d" % x for x in sorted(cuenta.items())))
if difs:
    print()
    print("!!! %d codigos con estado DISTINTO entre el generador y la pantalla:" % len(difs))
    for d in difs[:20]:
        print("   ", " | ".join(str(x) for x in d))
    sys.exit("Las dos reglas se desincronizaron. Hay que igualarlas antes de publicar.")
print()
print("Las dos reglas coinciden en los %d codigos." % len(D["rows"]))
