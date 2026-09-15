# CLAUDE.md — Proyecto Dashboard Forecast (Electroestrada)

Contexto del proyecto. El trabajo se hace en **Claude Code sobre Windows**
(antes se hacía en Cowork; esa etapa está cerrada).

## Qué es

Dashboard de compras y producto (motores de arranque, alternadores y repuestos):
forecast por código, liquidación, proyección e histórico. Es un único HTML
autocontenido —funciona offline y se puede mandar por mail o WhatsApp— que además se
publica en GitHub Pages.

- Dashboard: `Dashboard_Forecast.html` (en esta carpeta)
- Publicar: `Subir_a_GitHub.bat` (doble clic)
- GitHub Pages: https://erik07-ee.github.io/Dashboard-Forecast/Dashboard_Forecast.html
- Repo: https://github.com/Erik07-EE/Dashboard-Forecast
- Git: erik@electroestrada.com.ar / Erik07-EE

## Cómo trabajar (IMPORTANTE)

Cuando Erik diga **«actualizar»** — a secas, o «actualiza el dashboard», «actualizá los
costos», lo que sea — seguir la skill `forecast-dashboard`, que se carga sola al abrir
esta carpeta. **No preguntarle qué actualizar:** siempre es todo (bajar el Gestor de
precios, regenerar desde el Forecast.xlsm, chequear y dejarlo listo para publicar).

- `.claude/skills/forecast-dashboard/` — flujo, pestañas y reglas
- `.claude/skills/forecast-dashboard-tech/` — estructura de los Excel y detalle técnico
- `scripts/generar_dashboard.py` — lee los Excel y arma el HTML
- `scripts/plantilla.html` — **la fuente única de la UI**
- `scripts/chequear_actualizacion.py` — revisa los datos antes de publicar

**La lógica vive en los scripts, no en el chat.** Si algo hay que cambiar, se corrige el
script o la plantilla y queda arreglado para siempre; no reescribir el HTML a mano.

Reglas que no se negocian:

- **NUNCA** editar `Dashboard_Forecast.html` a mano: se regenera entero. Los cambios de
  UI o de lógica van **siempre** en `scripts/plantilla.html`.
- **NUNCA** publicar sin correr `scripts/chequear_actualizacion.py`. Si avisa que el
  stock va para atrás, **frenar y preguntarle a Erik**.
- **NUNCA** saltear la validación del JS (`node --check`) después de tocar la plantilla.
- Cambios grandes: mostrar un preview y esperar el OK antes de aplicarlos.

⚠️ `Subir_a_GitHub.bat` hace `git add -A`: commitea **todo** lo que esté modificado en la
carpeta. No dejar cambios a medio hacer cuando se le pide a Erik que publique.

## Estructura de la carpeta

```
Dashboard_Forecast.html       el dashboard (NO MOVER: la URL pública apunta acá)
Subir_a_GitHub.bat            publicar (NO MOVER: se usa con doble clic)
CLAUDE.md                     este archivo (NO MOVER: Claude Code lo lee de la raíz)
.nojekyll                     NO BORRAR: sin esto GitHub Pages no publica
.claude/skills/               instrucciones del proyecto, se cargan solas
scripts/                      el generador, la plantilla y el chequeo
Historial/                    cómo se llegó hasta acá y por qué (NO se publica: es interno)
```

⚠️ El repo de GitHub es **público**. `Historial/` está en `.gitignore` a propósito:
es documentación interna y **no debe subirse**. No sacarlo del `.gitignore`.

`Historial/Historial_Proyecto.md` es el resumen de la etapa Cowork (jul–sep 2026): qué se
construyó, qué criterios se definieron y por qué. **Leerlo antes de cambiar una regla de
negocio.** El estado actual, en cambio, está en este archivo.

## Entorno

| | |
|---|---|
| Sistema | Windows 11 |
| Python | 3.12 con `openpyxl` — lee los Excel y arma el HTML |
| Node.js | v24 en `C:\Program Files\nodejs\node.exe` (no está en el PATH de bash) |
| Google Drive | unidad `G:` — desde Claude Code los Excel se leen bien |

Las fuentes de datos son dos:

- **Forecast.xlsm** en Drive:
  `G:\Unidades compartidas\7. Compras y producto\7.3. Compras\7.3.3. Rotación\Forecast\Forecast.xlsm`
- **Gestor de precios**: Google Sheet «Gestor de precios - DATOS»
  (id `1-X6PyLTioEo_mhMI_P2hKq5zIOywnsIkOPGfKFYRg2Y`). Es **privado**, así que el `.bat` no
  puede bajarlo: lo baja Claude con el conector de Drive y deja la copia en
  `scripts/costos_gestor.xlsx`. Esa copia está en `.gitignore` — es el master de costos y
  márgenes de la empresa y el repo es público.

⚠️ El viejo `Costos.xlsm` quedó **obsoleto el 14/09/2026**. Ya no se lee. Si alguien lo
sigue actualizando, ignorarlo: la verdad está en el Sheet.

**El circuito de los costos lo eligió Erik el 14/09 y es este** (no proponerle otro):
cuando actualiza algo en el Gestor, **le pide a Claude que baje la planilla**, Claude
regenera, y después él publica con el `.bat`. Se evaluaron dos formas de que el `.bat`
bajara el Sheet solo — un Apps Script que exporte a Drive, o una credencial de Google en
la PC — y las descartó: prefiere el paso manual.

## Estado actual (14/09/2026)

- Proyecto ordenado y migrado a Claude Code. El generador pasó de `Generador/` a `scripts/`.
- Dashboard regenerado con **stock del lunes 14/09/2026 06:37**: 5.528 códigos, 38 GA con
  IMPO, histórico de 7 meses (feb–ago 2026).
- Se sumó el chequeo previo a publicar, después de que el 14/09 el stock saliera del 04/09
  cuando lo publicado ya era del 07/09.

- Carpeta limpiada: se borraron las copias en PDF de las skills y el prompt viejo de
  Cowork (`Instrucciones_Proyecto.docx`), todo reemplazado por este archivo y
  `.claude/skills/`. Siguen recuperables desde el historial de git si hicieran falta.
- Confidencialidad: Erik decidió (14/09) **dejar el dashboard público como está**. Ver
  abajo.
- **Costos migrados al Gestor de precios (14/09).** El `Costos.xlsm` quedó obsoleto. El
  CMM ya no lo calcula el dashboard: lo trae del Gestor. Resultado del cambio: 3.943
  códigos con el CMM casi igual, 1.535 que cambian (0,6 puntos típico, por costos más
  frescos) y 46 genéricos «reconstruidos» que salen de Liquidación por no tener CMM
  cargado — correcto según Erik: son códigos de uso especial, no llevan ese dato.
- La venta real ahora sale **solo** de la hoja `V.R. mensual` del Forecast.xlsm. Se eliminó
  el respaldo a un archivo suelto: uno viejo olvidado en la carpeta pisaba el dato bueno.

Pendientes que vienen del Excel (ver `Historial/Historial_Proyecto.md`):

- [x] Fórmula "Meses fin de mes" corregida (numerador = Stock ini + Compra − VP).
      Verificado el 14/09 en el Forecast.xlsm: **5.581 filas × 12 meses, todas OK**.
      MA-0040 (fila 12) da 0.0 en septiembre, como se esperaba.
- [x] Doble estacionalidad en la Venta proyectada, **corregida el 14/09**. La condición
      del IF multiplicaba la demanda por estacionalidad y evento cuando la demanda **ya
      los traía**, así que proyectaba ventas por encima del stock disponible. Afectaba a
      326 códigos y 849 unidades al año. Se sacó el `*estac$2*evento$2` de la condición,
      en las 12 columnas × 5.581 filas. Verificado: 0 casos mal.

Ya no quedan pendientes del Excel.

## Pestaña Stock y modelo mín/máx (14/09/2026)

Se sumó la solapa **Stock** y, con ella, se unificó el criterio de todo el dashboard.
El detalle técnico está en las dos skills; acá queda lo que hay que **no** deshacer:

- **Un solo ritmo.** Meses y unidades se convierten con la *Venta ajustada* (col BV,
  índice 106 de `rows[]`), la misma base del `Meses actual` del Excel. Antes Stock y
  Acción comercial sumaban la venta proyectada de N meses y se contradecían con el punto
  rojo del Forecast en el **42%** de los códigos; ahora el desacuerdo es de 12 casos, todos
  pegados al límite por redondeo.
- **El mínimo es una regla, no un número a mano.** Importados: máximo − 1 mes. El resto:
  la mitad del máximo. Se sacó el control "Alerta! Meses mínimo = ..." del tab Forecast.
  **Por qué:** con −1 mes fijo, 3.593 SKU (el 65%) quedaban con mínimo cero y **nunca**
  podían disparar la alerta — 2.241 de ellos ya estaban quebrados sin aviso. Los Importados
  no tenían ese problema (sus máximos son de 2 a 4 meses), por eso conservan el −1 mes.
- **Vocabulario cerrado:** Quiebre · Riesgo · Ideal · Exceso. Y lo que se llamaba "Ideal"
  (col H) ahora es **Máximo** en toda la interfaz.
- Stock y Acción comercial **comparten 5 columnas a propósito** (stock, exceso, meses y su
  valorización): Stock responde "cómo estoy", Acción "a qué descuento lo saco". Erik lo
  evaluó y decidió dejarlo así.

También se limpió la interfaz a pedido suyo: sin textos de ayuda, sin el botón PDF, sin el
conteo de candidatos, sin la columna "Meses máx" en Acción comercial (preview **y** Excel,
que pasó a 29 columnas), barra de filtros en un renglón y solapas fijas al scrollear.

## La interfaz, como quedo el 14/09

Erik la ajusto pantalla por pantalla. **No volver atras sin que el lo pida:**

- **Solapas:** Forecast · Estado Stock · Acción comercial · Proyección · Histórico.
- **Forecast:** GA · Código · Cat · **Packaging** · **Stock hoy** · **Meses hoy**. UN y
  "Meses máx" ya no se muestran (el dato se sigue usando para el mínimo y los estados).
- **Estado Stock:** tabla de **15 filas**. El **Faltante va abierto por estado**:
  Quiebre y Riesgo con costo a invertir **y** mix que se podría vender; "Hasta el
  máximo" **solo el costo**, porque esos códigos ya tienen stock para vender.
- **Acción comercial:** sin "Meses máx", sin "Costo total", sin botón PDF, sin conteo de
  candidatos ni título de preview. El Excel quedo en **28 columnas**.
- Sin textos de ayuda en ninguna solapa. Barra de filtros en un renglón, solapas fijas.

⚠️ **Dos trampas del HTML, por si hay que tocarlo:**

1. **La fila de TOTALES de Acción comercial tiene las celdas contadas a mano.** Si se
   agrega o saca una columna, hay que ajustarla o los totales quedan corridos de lugar.
2. **El Excel de Acción comercial va por índices fijos** (colores, anchos, formatos y
   merges atados al número de columna). Sacar una del medio obliga a renumerar todo:
   conviene reescribir `exportLiqXlsx` entera y verificar el resultado, no parchearla.

**El scroll lateral del Forecast** engancha al inicio de cada mes. Costó tres intentos,
así que conviene leer por qué antes de tocarlo:

- El enganche es `scroll-snap` con `scroll-padding-left` = ancho del bloque fijo (`--idw`).
- **Todo se mide del HTML, nunca se calcula.** El bloque fijo no mide la suma de los
  anchos declarados (la tabla estira GA) y los meses no arrancan donde uno supone: en
  1280px arrancan en 593,9 y no en 538. Al medir hay que **sumarle el `scrollLeft`**, y no
  forzar `scrollLeft=0` porque el propio enganche lo impide.
- El tope del scroll no caía en ningún enganche, así que se le agrega **aire al final**
  (margen derecho de la tabla) hasta el primer punto de enganche posterior. Apuntar al
  último mes en vez de al siguiente enganche deja un vacío enorme en pantallas anchas.
- Va en `setTimeout`, no en `requestAnimationFrame`: rAF no corre con la pestaña en
  segundo plano y la calibración quedaba sin hacer.
- El nombre del mes y su selector van juntos dentro de `.mhold`, que es lo pegajoso. Si se
  los pega por separado, se superponen.
- La última columna fija lleva borde y sombra (`.idend`) — esa sombra **debe** incluir el
  `inset 0 -3px 0` amarillo o se pierde la línea del encabezado.

Verificado en 1280 y 1680 px, en todas las posiciones de scroll: ninguna columna cortada.

## Datos del Excel que conviene mirar
- **6 códigos con venta ajustada negativa** (más devoluciones que ventas): IB2810.40,
  IMI2509.10, IV2313.10, RV099.30, BB1010.30, BDE0906.30. Dan meses de cobertura absurdos
  (hasta −108). No rompen nada, pero el número que se ve no tiene sentido.
- **1.687 códigos con la receta de costo incompleta** en el Gestor: el costo sale más bajo
  de lo real y con él el CMV y la liquidación. Erik los va completando.

## Mejoras: todas anuladas el 14/09

Erik revisó la lista de `Historial/Mejoras_Dashboard_Forecast.pdf` y **anuló las 6**.
**No volver a proponerlas** salvo que él las traiga:

1. ~~Confidencialidad~~ (sacar costos/márgenes o poner login) — deja el dashboard público.
2. ~~Validar la estructura del Excel al generar~~
3. ~~Alertas / KPIs arriba~~
4. ~~Automatizar la generación~~ (tarea programada)
5. ~~Toggle de moneda~~ (USD / pesos)
6. ~~Histórico acumulado~~ (exportar a Excel para tendencias multi-año)

**No queda ninguna mejora abierta.** El proyecto está cerrado en su alcance actual: se
usa para actualizar y publicar el dashboard, nada más.

## Confidencialidad (decidido el 14/09)

El dashboard está público en GitHub Pages **con códigos, costos y márgenes adentro**.
Erik lo sabe y eligió dejarlo así por ahora. **No volver a plantearlo salvo que él lo
traiga.** Si alguna vez se retoma, las opciones eran: sacar costos/márgenes de la versión
pública, o mover el hosting a uno con login.

Sí se sacó del repo la documentación interna (`Historial/`, vía `.gitignore`).

## Preferencias del usuario

Erik gestiona compras y producto. **No es programador.**

1. **Paso a paso claro y corto.** Nada de tecnicismos, comandos ni rutas salvo que los
   necesite él. Mencionar un problema técnico solo si cambia una decisión suya.
2. Respuestas concisas, **en español**. No hace falta tanto texto.
3. Ofrecer **checklist de opciones** cuando haya que decidir algo.
4. Cada 5 preguntas, hacer un resumen simple de lo hablado.
5. Antes de generar algo, mostrarlo para revisión.
