# -*- coding: utf-8 -*-
"""Congela la foto de un mes a partir del Dashboard_Forecast.html ya publicado.

⚠️ POR QUE EXISTE: la foto de septiembre se habia guardado antes de que existiera el
detalle por codigo, y Erik pidio el 18/09 congelarla **hoy**: *"Septiembre ya congelalo
en historico, si manana cambian los valores no importa, pero necesito que septiembre se
congele a hoy"*. Como septiembre ya figuraba en el archivo, `foto_mensual` no lo volvia
a escribir (y esta bien que no lo haga: esa es justamente la regla).

Este script es el destapador para esa unica vez. Toma el DATA del dashboard **que esta
publicado**, asi la foto congelada es exactamente lo que se ve hoy en pantalla, y no el
resultado de otra corrida.

De octubre en adelante no hace falta: la foto la saca sola `foto_mensual` en la primera
corrida del mes.

Se corre con:  python scripts/congelar_septiembre.py 2026-09
"""
import io
import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import generar_dashboard as G

MES = sys.argv[1] if len(sys.argv) > 1 else None
if not MES:
    sys.exit("Falta el mes. Ej: python scripts/congelar_septiembre.py 2026-09")

HTML = os.path.join(BASE, "Dashboard_Forecast.html")
RUTA = os.path.join(SCRIPTS, "historico_stock.json")

s = io.open(HTML, encoding="utf-8").read()
i = s.index("const DATA =") + len("const DATA =")
D = json.loads(s[i:s.index("\n", i)].rstrip().rstrip(";"))

iso = D.get("stock_iso") or ""
if iso[:7] != MES:
    sys.exit("El dashboard tiene stock de %s y se pidio congelar %s. Freno." % (iso[:7], MES))

hist = json.load(open(RUTA, encoding="utf-8")) if os.path.exists(RUTA) else {}
antes = hist.get(MES)

ga, cod = {}, {}
for r in D["rows"]:
    k = G.estado_de(r, D)
    cod[r[2]] = G.LETRA[k]
    g = ga.setdefault(D["GA"][r[1]], {}).setdefault(k, {"n": 0, "u": 0, "c": {}})
    g["n"] += 1
    g["u"] += r[4] or 0
    cc = (D.get("costos") or {}).get(r[2])
    if cc and cc[0] is not None and (r[4] or 0) > 0:
        cur = cc[3] if len(cc) > 3 and cc[3] else "$"
        g["c"][cur] = round(g["c"].get(cur, 0) + (r[4] or 0) * cc[0], 2)

hist[MES] = {"fecha": iso, "ga": ga, "cod": cod}
with open(RUTA, "w", encoding="utf-8") as f:
    json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))

tot = {}
for g in ga.values():
    for k, v in g.items(): tot[k] = tot.get(k, 0) + v["n"]
print("Foto de %s congelada desde el dashboard publicado (stock %s)" % (MES, iso))
print("  %s  | %d codigos con detalle" % (
    " ".join("%s %d" % x for x in sorted(tot.items())), len(cod)))
if antes:
    viejo = {}
    for g in antes.get("ga", {}).values():
        for k, v in g.items(): viejo[k] = viejo.get(k, 0) + v["n"]
    if viejo != tot:
        print("  ⚠️ La foto anterior decia: %s" % " ".join("%s %d" % x for x in sorted(viejo.items())))
    else:
        print("  Los totales no cambiaron; lo que se agrego es el detalle por codigo.")
print("  Archivo: %.1f KB" % (os.path.getsize(RUTA) / 1024.0))
