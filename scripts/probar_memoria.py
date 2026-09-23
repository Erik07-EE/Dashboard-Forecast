# -*- coding: utf-8 -*-
"""Prueba de la memoria del mes, simulando el caso que le preocupa a Erik.

REDB-111 hoy: stock al 1ro 0, stock hoy 1, demanda 31. La perdida da 30.
Manana vende esa unidad y queda en 0. Sin memoria la perdida volvia a 31, porque la
unidad entro y salio entre dos fotos y el dashboard nunca la vio.

Se simulan tres corridas encadenadas sobre el HTML real (no sobre datos inventados):
  1. la foto de hoy            -> acumulado 0
  2. la misma foto otra vez    -> no debe sumar nada (mismo Excel, idempotente)
  3. una foto mas nueva con REDB-111 en 0 -> debe registrar la baja de 1
Y una cuarta con una foto MAS VIEJA, que no debe tocar nada. Mas el cambio de mes.

Se corre con:  python scripts/probar_memoria.py
"""
import copy
import datetime
import io
import json
import os
import sys
import tempfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)
import generar_dashboard as G

# Se trabaja sobre el dashboard real, en una copia en el temporal del sistema: la prueba
# NO debe tocar el Dashboard_Forecast.html ni dejar nada en la carpeta del proyecto.
PREV = os.path.join(BASE, "Dashboard_Forecast.html")
TMP = os.path.join(tempfile.gettempdir(), "_memoria_test.html")
if not os.path.exists(PREV):
    sys.exit("No esta %s: hay que generar el dashboard antes de correr la prueba." % PREV)


def leer(p):
    s = io.open(p, encoding="utf-8").read()
    i = s.index("const DATA =") + len("const DATA =")
    return json.loads(s[i:s.index("\n", i)].rstrip().rstrip(";")), s


def escribir(data, path, base_html):
    i = base_html.index("const DATA =") + len("const DATA =")
    j = base_html.index("\n", i)
    io.open(path, "w", encoding="utf-8").write(
        base_html[:i] + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + base_html[j:])


def correr(iso, dias):
    """Una fecha de stock movida `dias` respecto de `iso`, en el mismo formato.

    ⚠️ Las fechas NO pueden ir escritas a mano: el dashboard se regenera todo el tiempo
    y una fecha fija que hoy es "mañana" en dos dias queda en el pasado, la memoria la
    toma como foto vieja y la prueba falla sin que nada este roto. Paso el 17/09.
    """
    d = datetime.datetime.strptime(iso[:10], "%Y-%m-%d") + datetime.timedelta(days=dias)
    return d.strftime("%Y-%m-%d") + " 09:00"


def fila(data, cod):
    for r in data["rows"]:
        if r[2] == cod:
            return r
    raise KeyError(cod)


base, html = leer(PREV)
r = fila(base, "REDB-111")
print("Punto de partida  REDB-111: stock 1ro=%s  stock hoy=%s  demanda=%s  acumulado=%s"
      % (r[6], r[4], r[79], r[G.VACU] if len(r) > G.VACU else "-"))
print("   foto:", base["stock_iso"])

# --- corrida 2: el MISMO Excel. No hay foto nueva, no debe sumar nada.
d2 = copy.deepcopy(base)
for x in d2["rows"]:
    del x[G.VACU]
escribir(base, TMP, html)
G.aplicar_memoria(d2, TMP)
assert fila(d2, "REDB-111")[G.VACU] == (base["rows"] and [r for r in base["rows"] if r[2]=="REDB-111"][0][G.VACU]), "arrastro mal"
print("   OK: repetir el mismo Excel no inventa ventas\n")

# --- corrida 3: foto mas nueva, REDB-111 vendio su unica unidad
#
# ⚠️ El escenario se ARMA, no se toma del dashboard del dia. Antes se daba por sentado
# que REDB-111 tenia stock 1 y acumulado 0, que era cierto el 17/09 y dejo de serlo en
# cuanto la memoria empezo a acumular de verdad: el 23/09 el codigo ya venia con stock 0
# y acumulado 1, y la prueba fallaba sin que nada estuviera roto. Es la misma trampa que
# las fechas escritas a mano. La foto anterior se fabrica con los valores del caso.
def sembrar(data, cod, stock, acumulado):
    r = fila(data, cod)
    r[4] = stock
    while len(r) <= G.VACU:
        r.append(0)
    r[G.VACU] = acumulado
    return r


prev = copy.deepcopy(base)
p = sembrar(prev, "REDB-111", 1, 0)
p[79] = 31                 # demanda
p[6 + 3] = 0               # venta proyectada del Excel (col CK)
sembrar(prev, "VRI-1515", 114, 0)
sembrar(prev, "PB225", 100, 0)
escribir(prev, TMP, html)

d3 = copy.deepcopy(prev)
for x in d3["rows"]:
    del x[G.VACU]
d3["stock_iso"] = correr(prev["stock_iso"], 1)
fila(d3, "REDB-111")[4] = 0                      # 1 -> 0
fila(d3, "VRI-1515")[4] = 100                    # 114 -> 100
fila(d3, "PB225")[4] = 105                       # sube: no debe restar
G.aplicar_memoria(d3, TMP)
a = fila(d3, "REDB-111")
perdida = max(0, a[79] - max(a[6 + 3] or 0, a[G.VACU] + a[4]))
print("   REDB-111  stock hoy=%s  acumulado=%s   -> venta en curso = %s"
      % (a[4], a[G.VACU], max(a[G.VACU], max(0, a[6] - a[4]))))
print("   perdida = demanda %s - max(vp %s, encurso+stock %s) = %s"
      % (a[79], a[6 + 3], a[G.VACU] + a[4], perdida))
assert a[G.VACU] == 1, a[G.VACU]
assert perdida == 30, perdida
assert fila(d3, "VRI-1515")[G.VACU] == 14, fila(d3, "VRI-1515")[G.VACU]
assert fila(d3, "PB225")[G.VACU] == 0, "un alza de stock no puede contar como venta"
print("   OK: la unidad que entro y salio quedo contada; la perdida da 30\n")

# --- corrida 4: alguien regenera con un Excel MAS VIEJO
escribir(d3, TMP, html)
d4 = copy.deepcopy(d3)
for x in d4["rows"]:
    del x[G.VACU]
d4["stock_iso"] = correr(base["stock_iso"], -1)
fila(d4, "REDB-111")[4] = 1
G.aplicar_memoria(d4, TMP)
assert fila(d4, "REDB-111")[G.VACU] == fila(d3, "REDB-111")[G.VACU], "conto de nuevo con un Excel viejo"
print("   OK: con un Excel mas viejo se arrastra lo acumulado, no se cuenta de nuevo\n")

# --- corrida 5: cambio de mes
escribir(d3, TMP, html)
d5 = copy.deepcopy(d3)
for x in d5["rows"]:
    del x[G.VACU]
d5["stock_iso"] = correr(base["stock_iso"], 40)
G.aplicar_memoria(d5, TMP)
assert fila(d5, "REDB-111")[G.VACU] == 0
print("   OK: al cambiar de mes arranca de cero\n")

os.remove(TMP)
print("Las 5 situaciones pasan.")
