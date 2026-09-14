# -*- coding: utf-8 -*-
"""
Compara el dashboard recien generado contra el que ya esta publicado y avisa si
algo no cierra ANTES de subirlo a GitHub.

Lo que chequea:
  1. Que la fecha del stock (celdas BN2/BO2 del Forecast.xlsm) no vaya para atras.
     Paso el 14/09/2026: el Excel tenia stock del 04/09 y lo publicado era del 07/09.
  2. Que el dashboard tenga datos (codigos > 0).
  3. Que la copia local del Gestor de precios (costos y CMM) no este vieja.

Salida:
  0 = todo bien, se puede publicar
  2 = hay una advertencia, conviene que Erik confirme
  1 = error (no se pudo leer alguno de los dos archivos)

Uso:  python scripts/chequear_actualizacion.py [Dashboard_Forecast.html]
"""
import io
import json
import os
import re
import subprocess
import sys
import time

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
         "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def leer_data(html):
    """Saca el objeto DATA embebido en el HTML del dashboard."""
    m = re.search(r"const DATA\s*=\s*(\{.*?\})\s*;", html, re.S)
    if not m:
        raise ValueError("no se encontro el bloque DATA en el HTML")
    return json.loads(m.group(1))


def fecha_stock(texto):
    """'Viernes 04 de Septiembre 2026 / 06:41 hs' -> (2026, 9, 4, 6, 41).

    Devuelve None si el texto no tiene el formato esperado (asi el chequeo no
    frena la publicacion por un cambio de formato)."""
    if not texto:
        return None
    m = re.search(r"(\d{1,2})\s+de\s+([^\s\d]+)\s+(\d{4})", texto)
    if not m:
        return None
    dia, mes_txt, anio = int(m.group(1)), m.group(2).lower(), int(m.group(3))
    mes_txt = (mes_txt.replace("á", "a").replace("é", "e").replace("í", "i")
                      .replace("ó", "o").replace("ú", "u"))
    if mes_txt not in MESES:
        return None
    hora, minuto = 0, 0
    mh = re.search(r"(\d{1,2}):(\d{2})", texto)
    if mh:
        hora, minuto = int(mh.group(1)), int(mh.group(2))
    return (anio, MESES.index(mes_txt) + 1, dia, hora, minuto)


def data_publicada(carpeta):
    """Lee el dashboard que esta publicado (ultima version subida a GitHub)."""
    try:
        crudo = subprocess.run(
            ["git", "show", "HEAD:Dashboard_Forecast.html"],
            cwd=carpeta, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if crudo.returncode != 0 or not crudo.stdout:
            return None
        return leer_data(crudo.stdout.decode("utf-8", "replace"))
    except Exception:
        return None


DIAS_COSTOS = 30   # a partir de aca la copia del Gestor se considera vieja


def revisar_costos(carpeta):
    """Avisa si la copia local del Gestor de precios quedo vieja o no esta.

    La baja Claude desde el chat (el Sheet es privado), asi que el .bat no puede
    refrescarla solo: lo unico que puede hacer es avisar."""
    ruta = os.path.join(carpeta, 'scripts', 'costos_gestor.xlsx')
    print('')
    if not os.path.exists(ruta):
        print('  Costos: FALTA la copia del Gestor de precios.')
        print('          El dashboard sale sin costos ni CMM.')
        print('          Pedile a Claude que baje la planilla.')
        return False
    dias = int((time.time() - os.path.getmtime(ruta)) / 86400)
    if dias > DIAS_COSTOS:
        print('  Costos: la copia del Gestor es de hace %d dias.' % dias)
        print('          Conviene que Claude la baje de nuevo antes de publicar.')
        return False
    print('  Costos: copia del Gestor de hace %d dia(s). Al dia.' % dias)
    return True


def main():
    carpeta = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(carpeta, "Dashboard_Forecast.html")

    try:
        nuevo = leer_data(io.open(ruta, encoding="utf-8").read())
    except Exception as e:
        print("ERROR: no se pudo leer el dashboard nuevo (%s)" % e)
        return 1

    costos_ok = revisar_costos(carpeta)
    viejo = data_publicada(carpeta)

    print("")
    print("  Dashboard recien generado:")
    print("    Fecha del stock : %s" % (nuevo.get("stock_ts") or "(sin fecha)"))
    print("    Codigos         : %s" % len(nuevo.get("rows") or []))
    print("    Generado        : %s" % (nuevo.get("gen") or "-"))

    if not nuevo.get("rows"):
        print("")
        print("  ATENCION: el dashboard salio SIN datos. No conviene publicarlo.")
        return 2

    if viejo is None:
        print("")
        print("  (No se pudo comparar con el dashboard publicado. Sigo igual.)")
        return 0 if costos_ok else 2

    print("")
    print("  Lo que ya esta publicado:")
    print("    Fecha del stock : %s" % (viejo.get("stock_ts") or "(sin fecha)"))
    print("    Codigos         : %s" % len(viejo.get("rows") or []))

    f_nueva, f_vieja = fecha_stock(nuevo.get("stock_ts")), fecha_stock(viejo.get("stock_ts"))
    if f_nueva and f_vieja and f_nueva < f_vieja:
        print("")
        print("  ================== ATENCION ==================")
        print("  El stock del dashboard nuevo es MAS VIEJO que el publicado.")
        print("")
        print("    publicado ahora : %s" % viejo.get("stock_ts"))
        print("    se publicaria   : %s" % nuevo.get("stock_ts"))
        print("")
        print("  Suele pasar por dos motivos:")
        print("    - no se volvio a pegar el stock de SAP en el Forecast.xlsm, o")
        print("    - si se pego, pero quedo vieja la fecha de las celdas BN2/BO2.")
        print("  ==============================================")
        return 2

    cambiadas = 0
    v_rows, n_rows = viejo.get("rows") or [], nuevo.get("rows") or []
    for i in range(min(len(v_rows), len(n_rows))):
        if v_rows[i] != n_rows[i]:
            cambiadas += 1

    v_cos, n_cos = viejo.get("costos") or {}, nuevo.get("costos") or {}
    cambiados_cos = sum(1 for k in n_cos if v_cos.get(k) != n_cos[k])

    print("")
    if cambiadas:
        print("  Cambiaron %s codigos (stock, compras, proyeccion)." % cambiadas)
    if cambiados_cos:
        print("  Cambiaron %s costos o CMM." % cambiados_cos)
    if not cambiadas and not cambiados_cos:
        print("  No cambio ningun dato: el dashboard publicado ya es el ultimo.")
    return 0 if costos_ok else 2


if __name__ == "__main__":
    sys.exit(main())
