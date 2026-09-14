---
name: forecast-dashboard
description: >-
  Actualizar y publicar el Dashboard Forecast de Electroestrada (compras/producto:
  motores de arranque, alternadores y repuestos). Usar cuando Erik diga
  **"actualizar", "actualiza", "actualizar dashboard", "actualiza el forecast",
  "actualiza los costos"** o cualquier variante de actualizar/regenerar/publicar el
  forecast, y también si pide cambios de UI o de lógica. Baja el Gestor de precios,
  regenera el HTML desde el Forecast.xlsm y lo deja listo para publicar en GitHub
  Pages. Complementaria: forecast-dashboard-tech.
---

# SKILL: forecast-dashboard

Instrucciones principales para actualizar/editar y publicar el Dashboard Forecast.

## Contexto
- **Salida:** `Dashboard_Forecast.html` (autocontenido). No editar a mano.
- **Plantilla (fuente única):** `scripts/plantilla.html` (HTML/CSS/JS; el dato va en `/*__DATA__*/`). **Editar siempre acá.**
- **Generador:** `scripts/generar_dashboard.py`. **Cache Histórico:** `scripts/historico_vp.json`.
- **Publicar:** doble clic en `Subir_a_GitHub.bat` (regenera → chequea → pide confirmación → push).
- **Chequeo previo:** `scripts/chequear_actualizacion.py` compara contra lo publicado y frena si el stock va para atrás. `.gitignore` excluye `__pycache__`; **`.nojekyll`** desactiva Jekyll en Pages (necesario: los PDF del repo rompían el build).
- **Repo:** https://github.com/Erik07-EE/Dashboard-Forecast · **Online:** https://erik07-ee.github.io/Dashboard-Forecast/Dashboard_Forecast.html

## Fuentes de datos (carpeta del Forecast en Drive)
- **Forecast.xlsm** (hoja Forecast): stock, VP, compras, IMPO, tendencia (AN), precio Mix (AS), venta real unidades (AB–AM), Caja x (col L), hoja **Estacionalidad**.
- **Gestor de precios** (Google Sheet «Gestor de precios - DATOS», hoja General, desde la fila 2):
  Código=B, **CMM %=F**, Moneda=H, Lista vigente=I, Costo=M. El Sheet es privado → lo baja
  Claude con el conector de Drive y deja la copia en `scripts/costos_gestor.xlsx` (no se sube
  al repo). El `Costos.xlsm` quedó **obsoleto el 14/09/2026**: no usarlo.
- **V.R. mensual.xlsx**: venta real facturada por código/mes, columna **$-USD** (USD para Importados, $ para Nacionales). Se arma desde Libro1.xlsx (SAP).
- **Forecast MM-AA** (fotos congeladas): en la **subcarpeta `Forecast\Histórico\`**. Para el Histórico. Se leen una vez (cache).

## Pestañas
- **Forecast:** tabla por código. Columnas de identidad: UN, GA, Código, Cat, Ideal, **Caja x** (col L), Stock, Meses. **Se pueden ocultar UN e Ideal** (× en el título; "mostrar N col." para restaurar). **Umbral del punto rojo editable** ("Alerta ● si Meses < Ideal − X", arriba de la tabla a la izquierda). Panel de pedidos IMPO con tarjeta "Proyectado".
- **Liquidación:** candidatos con exceso. Preview + Excel idénticos.
- **Proyección:** por mes VA c/stk, %, V.P.u, CMV, CMV/Vta, Venta $-USD. Encabezado con **Estac./Ev./TC editables** (simulador what-if: escala la proyección al instante; ↺ reset por mes) + CMV/TVP. Mes en amarillo/mayúscula.
- **Histórico:** por mes V.P.u/%/V.R.u/V.P.$/%/V.R.$. Encabezado con **TC editable** (vacío) que **totaliza el mes** = (Importados USD × TC) + Distribuidos $, con badge Real/Proy coloreado.

## Al decir «actualizar» (el caso normal)
Erik dice **«actualizar»** y con eso alcanza — no preguntarle qué actualizar. Hacer todo:

1. **Bajar el Gestor de precios** con el conector de Drive
   (`download_file_content`, fileId `1-X6PyLTioEo_mhMI_P2hKq5zIOywnsIkOPGfKFYRg2Y`,
   exportMimeType xlsx). La respuesta excede el límite de tokens y queda en un `.txt`:
   decodificar el base64 del campo `content` y guardarlo en `scripts/costos_gestor.xlsx`.
2. **Regenerar:** `python scripts/generar_dashboard.py "<Forecast.xlsm de G:>" Dashboard_Forecast.html`
3. **Chequear:** `python scripts/chequear_actualizacion.py`. Si avisa algo, frenar y preguntarle.
4. **Contarle qué cambió** y pedirle que corra `Subir_a_GitHub.bat` (publicar es de él).

## Flujo de trabajo (cambios de UI o lógica)
1. Cambios de UI/lógica: editar **solo `scripts/plantilla.html`** (string-replacement con `assert count==1`).
2. **Validar** el JS con `node --check` (ver skill técnica). No cerrar si falla.
3. Cambios grandes: **mostrar preview/mock y esperar OK**.
4. Regenerar y correr **`scripts/chequear_actualizacion.py`**. Si avisa que el stock va para atrás, **frenar y preguntarle a Erik**.
5. Pedir correr **`Subir_a_GitHub.bat`** + Ctrl+F5. Validar visual.
6. Al terminar: actualizar el estado en `CLAUDE.md` y, si cambió una regla, `Historial/Historial_Proyecto.md`.

## Flujo mensual del Histórico
A mes cerrado, tras sacar los pedidos, guardar una **copia congelada** del Forecast como `Forecast MM-26.xlsm` en `...\Forecast\Histórico\`. Se sigue trabajando en el `Forecast.xlsm` vivo. El `.bat` la suma una vez (cache).

## Reglas
- Respuestas concisas + checklist. Automatizaciones que se puedan enviar por mail/WhatsApp (el HTML es autocontenido; funciona offline).
- Editar la plantilla, nunca el HTML final. Validar visualmente antes de cerrar.

## Si GitHub Pages no publica
Verificar githubstatus.com (Actions/Pages). Si hay incidente, esperar; mientras, usar el HTML local (funciona offline).
