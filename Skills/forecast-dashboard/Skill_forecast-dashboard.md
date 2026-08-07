---
name: forecast-dashboard
description: >-
  Actualizar y publicar el Dashboard Forecast de Electroestrada (compras/producto:
  motores de arranque, alternadores y repuestos). Usar cuando el usuario diga
  "actualizar forecast", "regenerar dashboard forecast", "publicar forecast",
  "subir el forecast" o pida cambios de UI/lógica. Regenera el HTML desde los Excel
  y lo publica en GitHub Pages. Complementaria: forecast-dashboard-tech.
---

# SKILL: forecast-dashboard

Instrucciones principales para actualizar/editar y publicar el Dashboard Forecast.

## Contexto
- **Salida:** `Dashboard_Forecast.html` (autocontenido). No editar a mano.
- **Plantilla (fuente única):** `Generador/plantilla.html` (HTML/CSS/JS; el dato va en `/*__DATA__*/`). **Editar siempre acá.**
- **Generador:** `Generador/generar_dashboard.py`. **Cache Histórico:** `Generador/historico_vp.json`.
- **Publicar:** doble clic en `Subir_a_GitHub.bat` (regenera + push). `.gitignore` excluye `__pycache__`; **`.nojekyll`** desactiva Jekyll en Pages (necesario: los PDF del repo rompían el build).
- **Repo:** https://github.com/Erik07-EE/Dashboard-Forecast · **Online:** https://erik07-ee.github.io/Dashboard-Forecast/Dashboard_Forecast.html

## Fuentes de datos (carpeta del Forecast en Drive)
- **Forecast.xlsm** (hoja Forecast): stock, VP, compras, IMPO, tendencia (AN), precio Mix (AS), venta real unidades (AB–AM), Caja x (col L), hoja **Estacionalidad**.
- **Costos.xlsm** (hoja General): Costo=AC, Lista 1=J, Moneda=I, Q=17. CMM la calcula el dashboard con J.
- **V.R. mensual.xlsx**: venta real facturada por código/mes, columna **$-USD** (USD para Importados, $ para Nacionales). Se arma desde Libro1.xlsx (SAP).
- **Forecast MM-AA** (fotos congeladas): en la **subcarpeta `Forecast\Histórico\`**. Para el Histórico. Se leen una vez (cache).

## Pestañas
- **Forecast:** tabla por código. Columnas de identidad: UN, GA, Código, Cat, Ideal, **Caja x** (col L), Stock, Meses. **Se pueden ocultar UN e Ideal** (× en el título; "mostrar N col." para restaurar). **Umbral del punto rojo editable** ("Alerta ● si Meses < Ideal − X", arriba de la tabla a la izquierda). Panel de pedidos IMPO con tarjeta "Proyectado".
- **Liquidación:** candidatos con exceso. Preview + Excel idénticos.
- **Proyección:** por mes VA c/stk, %, V.P.u, CMV, CMV/Vta, Venta $-USD. Encabezado con **Estac./Ev./TC editables** (simulador what-if: escala la proyección al instante; ↺ reset por mes) + CMV/TVP. Mes en amarillo/mayúscula.
- **Histórico:** por mes V.P.u/%/V.R.u/V.P.$/%/V.R.$. Encabezado con **TC editable** (vacío) que **totaliza el mes** = (Importados USD × TC) + Distribuidos $, con badge Real/Proy coloreado.

## Flujo de trabajo
1. Cambios de UI/lógica: editar **solo `Generador/plantilla.html`** (string-replacement con `assert count==1`).
2. **Validar** el JS con `node --check` (ver skill técnica). No cerrar si falla.
3. Cambios grandes: **mostrar preview/mock y esperar OK**.
4. Pedir correr **`Subir_a_GitHub.bat`** + Ctrl+F5. Validar visual.
5. Al terminar: actualizar Prompt + Skills (.md/.pdf/.skill).

## Flujo mensual del Histórico
A mes cerrado, tras sacar los pedidos, guardar una **copia congelada** del Forecast como `Forecast MM-26.xlsm` en `...\Forecast\Histórico\`. Se sigue trabajando en el `Forecast.xlsm` vivo. El `.bat` la suma una vez (cache).

## Reglas
- Respuestas concisas + checklist. Automatizaciones que se puedan enviar por mail/WhatsApp (el HTML es autocontenido; funciona offline).
- Editar la plantilla, nunca el HTML final. Validar visualmente antes de cerrar.

## Si GitHub Pages no publica
Verificar githubstatus.com (Actions/Pages). Si hay incidente, esperar; mientras, usar el HTML local (funciona offline).
