---
name: forecast-dashboard-tech
description: >-
  Skill técnica complementaria de forecast-dashboard. Estructura de los Excel,
  fórmulas, índices de la fila de datos, simulador de Proyección, total del mes en
  Histórico, columnas dinámicas del tab Forecast, umbral del punto rojo, exclusiones
  y validación. Usar junto con la skill principal al editar/regenerar el dashboard.
---

# SKILL: forecast-dashboard-tech

Código, estructura y fórmulas del Dashboard Forecast.

## Rutas (bash VM)
- Plantilla: `.../Forecast/Generador/plantilla.html` (editar). HTML final: `.../Dashboard_Forecast.html` (no editar).
- Generador: `.../Generador/generar_dashboard.py`. Cache: `.../Generador/historico_vp.json`.
- Los Excel viven en Drive (G:); a veces no montan en bash → operar vía el `.bat`.

## Estructura Forecast.xlsm (hoja Forecast)
- Fila 3 headers; datos desde fila 6. Bloques mensuales **stride 14 desde col CJ(88)**: VP unidades=+1, VP USD=+4, Stock inicio=+5, Meses=+7, Cant. confirmada=+10.
- Identidad: UN=A, GA=B, Código=C, Cat=F, Meses/Cat (Ideal)=H, **Caja x=L (Cant.)**, Stock=BN, Meses=BO, Tendencia=AN, Precio Mix=AS.
- Venta real unidades: AB–AM (abs). Estac/Evento/TC del mes en fila 2 del bloque (offsets +9,+12,+4) — pero ver abajo.

## Fila de datos (índices en `rows[]`)
`[ui,gi,cod,cti,sa,ma]`(0-5) + flat 12×6 (6-77: si,mesesIni,compra,VP,stockFin,mesesFin) + `ideal`(78) + vpx 12×2 (79-102: base,USD) + `an`(103) + `pp`/mix(104) + **`cajax`(105)**. Constantes JS: `IDEAL=78`, `CAJAX=105`.

## Estacionalidad / Evento (fix importante)
Las celdas de estac/evento del Forecast son fórmulas `XLOOKUP` a la hoja **Estacionalidad** (A=mes, B=estac, C=evento). openpyxl (`data_only`) lee el **cache**, que puede quedar viejo. Por eso el generador **lee la hoja Estacionalidad directo** y redondea a **2 decimales** (`P2`), no a 1 — si no, 0.95 se convertía en 0.9 (95%→90%). Clave: `months[k]` (nombre del mes) → dict `_estac`.

## V.R. mensual (venta real)
Se arma desde `Libro1.xlsx` (SAP): Fecha=G, Código=O, Grupo=P, Cantidad=Q, Total S/Desc=U, TC=W. **Criterio $-USD:** TC>0 (Importados) → USD=Total/TC; TC=0 (Nacionales) → pesos=Total. `read_realusd` detecta el archivo con patrones `Venta_real*`,`Venta real*`,`V.R*`,`VR *`,`V R *`, y toma la subcolumna cuyo rótulo **contiene** "usd" (acepta `$-USD` y `USD`).

## Histórico (archivos congelados)
`build_historico` busca los `Forecast MM-AA.xlsm` en la **subcarpeta `Forecast\Histórico\`** (con/sin tilde), NO en la carpeta principal. Cache por mes (VP+MIX). VP$=MIX×VPu; VR$=venta real; %=(real−proy)/proy.

## Fórmulas
- Exceso (método B): ExcesoU = Stock − ΣVP(meses del Ideal); factor ×N; sólo >0.
- CMM=(J×0.7×0.93−Costo)/(J×0.7). CMM Liq con J×(1−DtoLiq). Dto Máx = mayor dto con contribución ≥ mín; Dto Liq = Máx − gap.
- Costo total=Costo×ExcesoU; Mix total=Mix×ExcesoU; Mix total Liq=Mix×(1−DtoLiq)×ExcesoU.

## Simulador Proyección (renderVP)
`st.simEstac{}`/`st.simEvento{}` por mes. `MULT[m]=(curE×curV)/(origE×origV)` (orig desde `DATA.season`). En `acc`, VP, venta USD y CMV se multiplican por `MULT[m]`; la base NO. Inputs Est./Ev. editables + `setSeasonSim`, `resetSeasonSimMonth` (↺ por mes). El export usa `_vpExport`, así refleja la simulación.

## Total del mes en Histórico (renderHist)
`st.histTC{}` por mes (vacío por defecto). `window._histSeg={impVP,impVR,distVP,distVR}` (segImp/segDist `.vpd`/`.vrd`). `recalcHist(i)`: VP=impVP×TC+distVP, VR=impVR×TC+distVR, %=(VR−VP)/VP coloreado (verde ≥0 `#0b7a3b`, rojo `#b3261e`). Sin TC → "–".

## Tab Forecast: columnas dinámicas + punto rojo
- Identidad config-driven `IDCOLS` (k,lbl,w,td); offsets sticky `left` calculados en JS (no CSS fijo). Sólo `hid:1` en `un` e `ideal` (× con `.colx` absoluta a la derecha; `showAllCols`). Ancho uniforme 70 en Ideal/Caja x/Stock/Meses.
- **Umbral punto rojo:** `st.dotGap` (def 2). `mcell` marca `d-red` si `v<ideal-st.dotGap`; el punto lleva `data-v/data-id/data-g`. `setDotGap`→`updateDots()` **repinta sin re-render** (no salta el scroll).

## Exclusiones
El generador **saltea el GA "Adicionales"** (`if str(row[1]).strip()=="Adicionales": continue`).

## Sticky (cuidado)
No poner `position:relative` en `th.mcol`: pisa el `position:sticky` y rompe el encabezado al scrollear. `sticky` ya sirve de ancla para hijos absolutos (botón reset).

## Patrón de parche + validación
Python exact-replace con `assert c.count(o)==1`. Validar SIEMPRE: extraer el `<script>`, reemplazar `/*__DATA__*/` por `null`, `node --check`. El código de datos (excU, MULT, recalcHist, offsets) probarlo con stubs en Node.

## Pages
`.nojekyll` en la raíz desactiva Jekyll (los PDF del repo con secuencias `{{`/`{%` rompían el build y dejaban Pages sirviendo la versión vieja).
