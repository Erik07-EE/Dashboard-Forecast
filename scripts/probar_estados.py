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


def mval(r, m, f): return r[6 + 6 * m + f]


def plata_en_pantalla(r, k):
    """Los dos montos de la tarjeta, transcriptos de stkCalc + CARDS en la plantilla."""
    cc = (D.get("costos") or {}).get(r[2])
    costo = cc[0] if (cc and cc[0] is not None) else None
    cur = (cc[3] if (cc and len(cc) > 3 and cc[3]) else "$")
    mix = r[104]
    stock = r[4] or 0
    maxU = r[108] or 0
    compraMes = mval(r, 0, 2) or 0
    exc = max(0, stock - maxU)
    falta = max(0, maxU - stock - compraMes)
    vend = max(r[109] or 0, max(0, (mval(r, 0, 0) or 0) - stock))
    perd = max(0, (r[79] or 0) - max(mval(r, 0, 3) or 0, vend + stock))
    excC = exc * costo if costo is not None else None
    excM = exc * mix if mix is not None else None
    falC = falta * costo if costo is not None else None
    perdM = perd * mix if (k in ("cero", "riesgo") and mix is not None) else None
    stkC = stock * costo if (costo is not None and stock > 0) else None
    stkM = stock * mix if (mix is not None and stock > 0) else None
    if k in ("cero", "riesgo"): return cur, falC, perdM
    if k == "ideal": return cur, falC, None
    if k == "exceso": return cur, excC, excM
    return cur, stkC, stkM                       # sinrot y lanz


difs = []
cuenta = {}
pg, pp = {}, {}      # plata segun el generador y segun la pantalla
for r in D["rows"]:
    a = G.estado_de(r, D)
    b = como_en_pantalla(r)
    cuenta[a] = cuenta.get(a, 0) + 1
    if a != b:
        difs.append((r[2], D["GA"][r[1]], "generador=%s" % a, "pantalla=%s" % b))
        continue
    for dest, (cur, c, m) in ((pg, G.plata_de(r, D, a)), (pp, plata_en_pantalla(r, a))):
        if c: dest[(a, "c", cur)] = dest.get((a, "c", cur), 0) + c
        if m: dest[(a, "m", cur)] = dest.get((a, "m", cur), 0) + m

print("Codigos comparados:", len(D["rows"]))
print("Reparto:", " ".join("%s %d" % x for x in sorted(cuenta.items())))
if difs:
    print()
    print("!!! %d codigos con estado DISTINTO entre el generador y la pantalla:" % len(difs))
    for d in difs[:20]:
        print("   ", " | ".join(str(x) for x in d))
    sys.exit("Las dos reglas se desincronizaron. Hay que igualarlas antes de publicar.")

# ⚠️ La plata de la foto tiene que ser LA MISMA que muestran las tarjetas. Si no, el
# historico contaria una pelicula distinta de la que se ve en Estado Stock.
malas = [k for k in set(pg) | set(pp) if round(pg.get(k, 0), 2) != round(pp.get(k, 0), 2)]
print()
if malas:
    print("!!! La plata no coincide en %d buckets:" % len(malas))
    for k in sorted(malas)[:12]:
        print("    %-24s generador %15.2f   pantalla %15.2f"
              % (" ".join(k), pg.get(k, 0), pp.get(k, 0)))
    sys.exit("plata_de() se desincronizo de las tarjetas. Igualarlas antes de publicar.")
print("Las dos reglas coinciden en los %d codigos, y la plata en los %d buckets."
      % (len(D["rows"]), len(set(pg) | set(pp))))
