---
name: forecast-dashboard
description: >-
  Actualizar y publicar el Dashboard Forecast de Electroestrada (compras/producto:
  motores de arranque, alternadores y repuestos). Usar cuando el usuario diga
  "actualizar forecast", "regenerar dashboard forecast", "publicar forecast",
  "subir el forecast" o variantes, o pida cambios de UI/lógica en el dashboard.
  Regenera el HTML desde los Excel y lo publica en GitHub Pages. Complementaria:
  forecast-dashboard-tech (código, estructura de Excel y fórmulas).
---

# SKILL: forecast-dashboard

Instrucciones principales para actualizar/editar y publicar el Dashboard Forecast.

## Contexto del Proyecto

- **Proyecto:** Forecast Compra-Venta mensual — Electroestrada
- **Salida final:** `Dashboard_Forecast.html` (un solo archivo, autocontenido). **No editar a mano.**
- **Plantilla (fuente única):** `generador/plantilla.html` (todo el HTML/CSS/JS; el dato se inyecta en `/*__DATA__*/`). **Editar SIEMPRE acá.**
- **Generador:** `generador/generar_dashboard.py` — lee los Excel y produce el HTML.
- **Cache Histórico:** `generador/historico_vp.json` (VP + MIX por mes de cada archivo congelado).
- **Script publicar:** `Subir_a_GitHub.bat` (doble clic: regenera + push).
- **Repo:** https://github.com/Erik07-EE/Dashboard-Forecast
- **Online:** https://erik07-ee.github.io/Dashboard-Forecast/Dashboard_Forecast.html
- **Git user:** erik@electroestrada.com.ar / Erik07-EE

## Fuentes de datos (Excel)

- **Forecast.xlsm** (hoja *Forecast*): stock, VP, compras, IMPO, estacionalidad, tendencia, venta real (AB–AM), precio ponderado/MIX (AS).
- **Costos.xlsm** (hoja *General*): Costo=AC, Lista 1=J, Moneda=I, Q(17)=lista futura. **La CMM la calcula el dashboard con J**, no se lee de Costos.
- **Forecast MM-AA** (archivos mensuales congelados): Histórico (VP=CJ+1, MIX por header). Se leen 1 vez → cache.
- **Venta_real*.xlsx**: venta real facturada por código/mes (USD) → columna V.R. $-USD del Histórico.

## Pestañas

Forecast · Liquidación · Proyección · Histórico. Filtros globales UN→GA→Categoría→Código. Vista de 4 meses con flechas ◀▶ en las 3 tablas mensuales.

## Flujo obligatorio (respetar el orden)

1. Para CUALQUIER cambio de UI/lógica: editar **solo `generador/plantilla.html`** (nunca el HTML final).
2. Aplicar el cambio con string-replacement quirúrgico (Python `assert count==1`; ver skill técnica).
3. **Validar el JS** con `node --check` sobre el `<script>` extraído (reemplazar `/*__DATA__*/` por `null`). No cerrar si falla.
4. Para cambios grandes: **mostrar preview/mock y ESPERAR OK** antes de aplicar.
5. Pedirle al usuario que ejecute **`Subir_a_GitHub.bat`** (regenera desde los Excel + publica) y haga Ctrl+F5.
6. **Validar visualmente** el resultado antes de cerrar.
7. Al terminar: actualizar **Memoria / Prompt / Skills (Word + PDF)** y recordar pegar el Prompt en las instrucciones del proyecto.

## Reglas de trabajo (preferencias de Erik)

- Respuestas concisas y claras; ofrecer opciones tipo checklist.
- Toda automatización debe poder enviarse por mail/WhatsApp (archivo).
- Las descargas de Excel deben ser **idénticas al preview** en pantalla.
- Editar la plantilla, nunca el HTML final; regenerar con el .bat.

## Convenciones visuales

- Marca: navy `#1a237e` + amarillo `#ffd600`, logo Electroestrada, Segoe UI.
- Encabezados: fondo azul, letra blanca, **línea amarilla como corte** entre encabezado y datos. Segmento **Liquidación** invertido (amarillo, letra azul).
- **Totales:** gris claro `#eceef7`, letra negra, importes con su color (Costo rojo, Mix/Obj verde).
- Excels con números en **formato Contabilidad USD / $**.
