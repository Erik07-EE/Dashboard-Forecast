# -*- coding: utf-8 -*-
"""Rearma la foto de un mes a partir de un Dashboard_Forecast.html ya generado.

⚠️ POR QUE EXISTE: de octubre en adelante la foto la saca sola `foto_mensual` en la
primera corrida del mes y nadie tiene que correr esto. Sirve para los casos en que un mes
quedo congelado con menos datos de los que hoy se guardan, y se lo puede reconstruir
**exacto** desde el dashboard de ese momento (el historial de git los tiene todos).

Asi se recupero septiembre el 23/09: la foto original no tenia la plata, y el dashboard
con el stock del 17/09 12:35 estaba en el commit caeae9e. Reconstruirla desde ahi no es
reescribir la historia -- es la misma foto, con los campos que faltaban.

    git show caeae9e:Dashboard_Forecast.html > /tmp/dash.html
    python scripts/congelar_mes.py 2026-09 /tmp/dash.html

Sin el segundo argumento usa el Dashboard_Forecast.html de la carpeta.
"""
import io
import json
import os
import sys

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import generar_dashboard as G

if len(sys.argv) < 2:
    sys.exit("Falta el mes. Ej: python scripts/congelar_mes.py 2026-09 [dashboard.html]")
MES = sys.argv[1]
HTML = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "Dashboard_Forecast.html")
RUTA = os.path.join(SCRIPTS, "historico_stock.json")

s = io.open(HTML, encoding="utf-8").read()
i = s.index("const DATA =") + len("const DATA =")
D = json.loads(s[i:s.index("\n", i)].rstrip().rstrip(";"))

iso = D.get("stock_iso") or ""
if iso[:7] != MES:
    sys.exit("Ese dashboard tiene stock de %s y se pidio congelar %s. Freno."
             % (iso[:7], MES))

hist = json.load(open(RUTA, encoding="utf-8")) if os.path.exists(RUTA) else {}
antes = hist.get(MES)

foto = G.foto_de(D)
foto["fecha"] = iso
hist[MES] = foto
with open(RUTA, "w", encoding="utf-8") as f:
    json.dump(hist, f, ensure_ascii=False, separators=(",", ":"))

tot, plata = {}, {}
for g in foto["ga"].values():
    for k, v in g.items():
        tot[k] = tot.get(k, 0) + v["n"]
        for campo in ("c", "m"):
            for cur, x in v.get(campo, {}).items():
                plata.setdefault((k, campo), {})
                plata[(k, campo)][cur] = plata[(k, campo)].get(cur, 0) + x

print("Foto de %s rearmada desde %s (stock %s)" % (MES, os.path.basename(HTML), iso))
print("  SKU: %s" % " ".join("%s %d" % x for x in sorted(tot.items())))
print("  %d codigos con detalle" % len(foto["cod"]))
print()
print("  %-8s %-28s %s" % ("estado", "costo", "venta mix"))
for k in ("cero", "riesgo", "ideal", "exceso", "sinrot", "lanz"):
    def pp(campo):
        d = plata.get((k, campo), {})
        return " ".join("%s %s" % (c, format(int(round(v)), ",d").replace(",", "."))
                        for c, v in sorted(d.items())) or "-"
    print("  %-8s %-28s %s" % (k, pp("c"), pp("m")))

if antes:
    viejo = {}
    for g in antes.get("ga", {}).values():
        for k, v in g.items(): viejo[k] = viejo.get(k, 0) + v["n"]
    print()
    if viejo != tot:
        print("  ⚠️ Los SKU por estado CAMBIARON respecto de la foto anterior:")
        print("     antes: %s" % " ".join("%s %d" % x for x in sorted(viejo.items())))
    else:
        print("  Los SKU por estado dan igual que antes: solo se agrego la plata.")
print("  Archivo: %.1f KB" % (os.path.getsize(RUTA) / 1024.0))
