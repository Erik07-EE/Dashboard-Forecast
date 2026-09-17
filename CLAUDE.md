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
- **El Forecast.xlsm se actualiza dos veces por día** (Erik sigue el stock de cerca). Que
  la fecha del stock cambie entre una regeneración y otra es lo normal, no un problema:
  el chequeo solo tiene que frenar si va **para atrás**.

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

- ⚠️ **El máximo sale del Excel (col CP «Stock máximo»), decidido el 17/09.** Es la suma
  de la demanda de los próximos *Meses por Cat.* meses, **cada uno con su estacionalidad**.
  Antes era `Meses por Cat. × Venta ajustada`, un ritmo plano que siempre daba más
  (MA-0002: 720 contra 562). **Consecuencia buscada por Erik:** el máximo ahora se mueve
  mes a mes — «sale un mes malo y puede entrar uno bueno» — así que un código puede pasar
  de Ideal a Exceso sin que se compre ni se venda nada.
  - Se usa **CP y no CB**: son el mismo concepto, pero CB está **mal calculada en 169
    códigos** (casi todos REDB) y da de más. Verificado contra la suma real mes a mes:
    CP acierta en los 169, CB en ninguno. CP además arranca en el mes en curso buscando
    la columna por el nombre del mes, así que sigue siendo correcta al correr el Forecast.
  - **El mínimo es la misma regla, en proporción sobre esa base**: Importados
    `máx × (H−1)/H`, el resto `máx × 0,5`. No se puede restar «un mes» en unidades porque
    los meses de CP no valen lo mismo entre sí.
  - ⚠️ **Acción comercial usa la MISMA base** (`excU` = stock − CP × nivel). Cuando solo
    cambió Estado Stock, 1.494 códigos mostraban un exceso distinto en cada solapa. Erik:
    «lo ideal es que todas las solapas vean el mismo valor». `idealU` se elimino: no debe
    volver a existir una función que calcule el máximo con el ritmo plano.
- **Un solo ritmo para los MESES.** *Meses actual* sigue siendo Stock / *Venta ajustada*
  (col BV, índice 106 de `rows[]`), igual que en el Excel. Antes Stock y
  Acción comercial sumaban la venta proyectada de N meses y se contradecían con el punto
  rojo del Forecast en el **42%** de los códigos; ahora el desacuerdo es de 12 casos, todos
  pegados al límite por redondeo.
- **El mínimo es una regla, no un número a mano.** Importados: máximo − 1 mes. El resto:
  la mitad del máximo. Se sacó el control "Alerta! Meses mínimo = ..." del tab Forecast.
  **Por qué:** con −1 mes fijo, 3.593 SKU (el 65%) quedaban con mínimo cero y **nunca**
  podían disparar la alerta — 2.241 de ellos ya estaban quebrados sin aviso. Los Importados
  no tenían ese problema (sus máximos son de 2 a 4 meses), por eso conservan el −1 mes.
- **Vocabulario cerrado:** Quiebre · Riesgo · Ideal · Exceso · Sin rotación · Lanzamientos. Y lo que se
  llamaba "Ideal" (col H) ahora es **Máximo** en toda la interfaz.
- ⚠️ **"Sin rotación" es un ESTADO, no un cruce** (16/09). Se evalúa **antes** que
  Riesgo/Ideal/Exceso, justo después de Quiebre. **Por qué:** un código que no vende tiene
  ritmo cero, así que su máximo da cero y **cae en Exceso por definición**. Erik lo vio al
  filtrar: tocaba "Sin rotación" y la tabla mostraba pastillas "Exceso". Eran **796 de los
  799**, con **$ 35 millones** que parecían compra de más y eran stock muerto. Exceso pasó
  de 2.491 SKU / $ 96,4M a **1.695 / $ 61,5M**. Los cinco ahora son excluyentes y suman 100%.
- ⚠️ **La plata de cada tarjeta va al bucket de SU estado** (`if(o.k==='exceso')add('excC'...)`).
  Sin esa condición el Exceso se come la de los sin rotación, que tienen exceso solo
  porque su máximo es 0.
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
- **Estado Stock:** sin torta (15/09): el reparto se lee en cada pastilla de estado,
  junto al conteo de SKU. Las pastillas quedaron con estado, conteo y %: el stock y el
  faltante/sobrante salieron de ahi, ya estan abiertos en las cajas de Faltante y Exceso.
  Tabla de **15 filas**. El **Faltante va abierto por estado**:
  Quiebre y Riesgo con costo a invertir **y** mix que se podría vender; "Hasta el
  máximo" **solo el costo**, porque esos códigos ya tienen stock para vender.
- **Acción comercial:** sin "Meses máx", sin botón PDF, sin conteo de candidatos ni título
  de preview. **"Costo total" volvió el 15/09** (Erik la pidió de vuelta): va en el grupo
  "Exceso $-USD", antes de "Mix total". El Excel quedo en **29 columnas**.
- Sin textos de ayuda en ninguna solapa. Barra de filtros en un renglón (más baja desde el
  15/09: desplegables de 24px), solapas fijas.
- ⚠️ **Los anchos de la tabla de Estado Stock (`COLS`) están calibrados**: Cat necesita
  46px (la pastilla mide 38 y con 30 salía con "…"), Estado 120 (la pastilla "Sin
  rotación" mide 92 + padding) y Meses hoy 72. Hay un `overflow:hidden;text-overflow:
  ellipsis` global en `th,td`, así que una columna corta recorta sin avisar.
- **La Cat, una sola pastilla en todo el dashboard** (fondo celeste grisáceo, letra azul).
  Antes cada letra tenía su color y en las tablas nuevas competía con el rojo del costo y
  el verde de la venta. Se pierde el golpe de vista A-vs-D: Erik lo eligió igual el 15/09.

⚠️ **Dos trampas del HTML, por si hay que tocarlo:**

1. **La fila de TOTALES de Acción comercial tiene las celdas contadas a mano.** Si se
   agrega o saca una columna, hay que ajustarla o los totales quedan corridos de lugar.
2. **El Excel de Acción comercial va por índices fijos** (colores, anchos, formatos y
   merges atados al número de columna). Sacar una del medio obliga a renumerar todo:
   conviene reescribir `exportLiqXlsx` entera y verificar el resultado, no parchearla.

**El scroll lateral del Forecast** engancha al inicio de cada mes. Costó tres intentos,
así que conviene leer por qué antes de tocarlo:

- **La causa de fondo, la que costó encontrar:** la tabla es `table-layout:auto` y
  **estira columnas según el contenido**. GA se declara en 110px y termina midiendo 165,9
  ("Motores de arranque" es largo). Los `left` de las columnas fijas salían de los anchos
  **declarados**, así que quedaban clavadas 56px antes de donde el bloque termina de
  verdad. De ahí venía todo: el panel «Stock al…» que parecía sobresalir, los meses
  corridos y la franja de columna cortada. Ahora los `left` se escriben en una hoja
  `#idcpos` (una regla `.idcpN` por columna) que el JS recalcula **midiendo el HTML**
  después de dibujar. Por clase y no celda por celda: son 5.500 filas.
- El enganche es `scroll-snap` con `scroll-padding-left` = ancho del bloque fijo (`--idw`),
  sin redondear: redondearlo corre el enganche un píxel y asoma una hilacha.
- **Todo se mide del HTML, nunca se calcula.** El bloque fijo no mide la suma de los
  anchos declarados (la tabla estira GA) y los meses no arrancan donde uno supone: en
  1280px arrancan en 593,9 y no en 538. Al medir hay que **sumarle el `scrollLeft`**, y no
  forzar `scrollLeft=0` porque el propio enganche lo impide.
- El tope del scroll no caía en ningún enganche, así que se le agrega **aire al final**
  (margen derecho de la tabla) hasta el primer punto de enganche posterior. Apuntar al
  último mes en vez de al siguiente enganche deja un vacío enorme en pantallas anchas.
- Va en `setTimeout`, no en `requestAnimationFrame`: rAF no corre con la pestaña en
  segundo plano y la calibración quedaba sin hacer.
- El nombre del mes y su selector van juntos dentro de `.mhold`, **centrados** sobre el
  bloque. Se probó hacerlos pegajosos para que no se escondieran al scrollear: no hace
  falta (el enganche ya evita que un mes quede a medias) y además los desalinea.
- La última columna fija lleva borde y sombra (`.idend`) — esa sombra **debe** incluir el
  `inset 0 -3px 0` amarillo o se pierde la línea del encabezado.

Verificado en 1280 y 1680 px, en todas las posiciones de scroll: ninguna columna cortada.

## Estado Stock: 5 tarjetas y una sola tabla (16/09/2026)

Los analisis empezaron como cuatro bloques desplegables aparte. Erik los fue llevando
**todos a la tabla** y al final no quedo ninguno: "no dupliquemos info". El recorrido
importa porque explica por que la tabla quedo como quedo.

### Las 5 tarjetas

Son **excluyentes y suman 100%**. Tocar una filtra la tabla. Cada una lleva dos bloques
de plata -- lo que cuesta y lo que se vende -- salvo Ideal, que solo lleva el costo.

| Tarjeta | Costo | Venta |
|---|---|---|
| Quiebre | Costo a invertir (maximo) | Venta mix perdida |
| Riesgo | Costo a invertir (maximo) | Venta mix perdida |
| Ideal | Costo a invertir (maximo) | -- |
| Exceso | Costo inmovilizado | Venta mix inmovilizado |
| Sin rotacion | Costo parado | Venta mix parado |

- ⚠️ **"Sin rotacion" es un ESTADO**, se evalua **antes** que Riesgo/Ideal/Exceso, justo
  despues de Quiebre. **Por que:** un codigo que no vende tiene ritmo cero, asi que su
  maximo da cero y **cae en Exceso por definicion**. Eran **796 de 799**, con **$ 35
  millones** que parecian compra de mas y eran stock muerto. Exceso paso de 2.491 SKU /
  $ 96,4M a 1.695 / $ 61,5M. Va **en gris**: es plata quieta, no una alarma.
- ⚠️ **La plata de cada tarjeta va al bucket de SU estado** (`if(o.k==='exceso')add('excC'...)`).
  Sin esa condicion el Exceso se come la de los sin rotacion.
- Las cajas "Faltante" y "Exceso de stock" se eliminaron: todo esta en su tarjeta.

### La tabla

Un solo lugar para todo. **Dos vistas** (boton "Ver"): por codigo, o **por grupo** --
cada fila un GA con sus totales, que se abre para ver sus codigos. Eso reemplazo a los
paneles de Exceso y de Quiebres.

Columnas: Producto (Grupo, Codigo, Cat, Fecha ing., **V.P. mes**, **Venta en curso**) ·
Stock (Min, Max, Stock hoy, Meses hoy, Estado) · **V.P. mensual perdida** (Unidades,
Venta mix) · Faltante (Unidades, Costo) · Exceso (Unidades, Costo, Venta mix).

- **V.P. mes** es la referencia que faltaba: min, max y meses salen todos de ese ritmo.
  En verde, porque es venta.
- ⚠️ **La venta perdida existe SOLO en Quiebre y Riesgo.** Lo pidio Erik y tiene razon:
  un codigo entre el minimo y el maximo esta cubierto, no puede "perder venta" y estar
  en Ideal al mismo tiempo. Ademas fuera de esos dos estados el numero era **ruido**:
  la venta proyectada del Excel arranca del **stock al 1ro** y el estado se juzga con el
  **stock de hoy**, asi que a mitad de mes marcaba perdidas donde hoy sobra stock
  (II2909.25: el 1ro tenia 2, hoy tiene 15, demanda 8 -- perdia 6 segun el Excel, y en
  realidad le sobra). En Quiebre y Riesgo el stock de hoy esta bajo el minimo, asi que
  ahi la perdida es real en los 245 casos.
- ⚠️ **Se mide con DEMANDA menos VENTA PROYECTADA.** Las columnas del Excel no se llaman
  como uno espera:
  - **demanda** = col CJ "V.Ajust. c/stock" (`r[79]`): lo que venderias al ritmo actual.
  - **venta proyectada** = col CK "Venta proy. (unidades)" (`mval(r,0,3)`): lo que si vas
    a vender, **contando las compras en camino**.
  La proyectada sola da **cero** justo en los peores quiebres (ASX11: demanda 1.316,
  proyectada 0) y la demanda sola cobra ventas que si vas a hacer cuando llegue el pedido
  (MA-4147: demanda 96, proyectada 89, perdes 7). **No volver a cambiarlo.**
- Faltante perdio "Venta mix": ese mix era el de vender hasta el maximo, o sea 3 o 4
  meses de venta en uno. Para cubrir el mes sirve el de la venta perdida.
- Se probo un "% del total" en Exceso: con 1.700 filas daba 0,02% en casi todas. Fuera.
- **Los GA se ordenan con la prioridad de los filtros** (`prioName`), no alfabeticamente,
  en las dos vistas. A igualdad, por codigo.
- ⚠️ **Los anchos (`COLS`) estan MEDIDOS, no estimados** (17/09). Hay un
  `overflow:hidden` global en `th,td`, asi que una columna corta **recorta sin avisar**.
  Como se miden, que es la unica forma que funciono:
  - Se pone la tabla en `table-layout:auto` con `width:max-content`, se quita el
    `colgroup` y se lee el ancho natural que resuelve **el propio navegador**.
  - Eso contempla solo dos cosas que a ojo (y midiendo con canvas) se escapan: el
    `text-transform:uppercase` de los encabezados, y los **encabezados de GRUPO con
    colspan** -- el de "Faltante (para llegar al stock maximo)" necesita 198 repartidos
    entre sus dos columnas, y por quedarse corto ahi se recorta el titulo.
  - Se toma el maximo de **tres** situaciones: por codigo, por grupo cerrado y por grupo
    abierto. ⚠️ La vista por grupo se llama **`'ga'`, NO `'grp'`**: medirla mal devuelve
    los mismos numeros que la de codigo y no se nota.
  - Se verifica despues con `scrollWidth > clientWidth` **y** `scrollHeight >
    clientHeight`: desde que el Grupo envuelve, una tercera linea se cortaria hacia
    abajo sin avisar.
  - Resultado: la tabla paso de 1.852 a **1.473 px**.
- ⚠️ **El Grupo va en 150px y el nombre ENVUELVE hasta 2 lineas** (`.st-ga` con
  `white-space:normal`). En una sola linea no bajaba de 199 por "Portaescobillas de
  alternador" en negrita en la vista por grupo. Erik prefirio partirlo. El 150 salio de
  medir cuantas filas se parten: 116 (el minimo posible) parte **2.430 filas, el 44%**;
  140 parte 805; **150 parte solo 194, los dos "Portaescobillas"**. Por 10px mas de
  ancho se parten 611 filas menos. Por debajo de 116 ya no entra en dos lineas:
  "Portaescobillas" es una sola palabra y no se puede cortar.

### Los 6 estados (17/09)

Se evaluan en este orden y son excluyentes:

| | Regla | Color |
|---|---|---|
| **Lanzamientos** | Cat **N o P**, sin importar el stock | azul |
| **Quiebre** | stock <= 0 | rojo |
| **Sin rotacion** | sin ventas en los 6 meses cerrados **y** sin movimiento este mes | gris |
| **Riesgo** | stock < minimo | naranja |
| **Exceso** | stock > maximo | amarillo |
| **Ideal** | el resto | verde |

- ⚠️ **Lanzamientos manda sobre todo.** Los **Cat P ("proximamente")** nunca tuvieron stock,
  asi que los 22 caian en Quiebre y lo ensuciaban con una falta que no es tal. Los **Cat N**
  van aparte porque "un C que no se vende no es lo mismo que un N que todavia no se
  exhibio": eran el 76% de los dolares de Sin rotacion. En la tarjeta el corte es **N · P**,
  no A · B.
- ⚠️ **La ventana de "sin ventas" son los 6 meses CERRADOS**, el mes en curso no esta. Por
  eso se mira aparte si el stock bajo desde el 1ro: si se movio, vendio, y no puede decir
  "sin ventas". Esos salen del estado y llevan un **punto verde** al lado del codigo (son
  1.733 en todo el dashboard).
- Cada tarjeta muestra **A y B** al lado del %: son las dos categorias que importan.

### El filtro Estado y los filtros cruzados (17/09)

- Hay un **quinto filtro global, "Estado"**, con los 6. Filtra las cinco solapas.
- **La tarjeta ES el filtro**: se guardan en `st.EST` y nada mas. Antes eran dos cosas
  distintas (`st.stFil` y la barra) y podian contradecirse dejando la tabla vacia sin
  explicacion. De paso se puede elegir mas de un estado.
- **Las tarjetas se calculan con `rowsBase()`** (todo menos el estado): si usaran
  `visibleRows()`, al filtrar por Quiebre las otras cinco darian cero.
- **Los cinco desplegables se achican entre si**, en cualquier orden (`rowsExcept`). Antes
  la cadena era fija UN -> GA -> CAT -> COD y se podia elegir Lanzamientos + Categoria D y
  quedaba vacio.
- ⚠️ **Lo ya elegido siempre se muestra, aunque cuente cero** (`conElegidos`). Si se cayera
  de la lista no habria forma de destildarlo.
- `stkOf` esta **memorizado** (`_skC`): con el filtro de estado se llamaba tres veces por
  render sobre 5.500 filas. La cache se tira sola si cambia el multiplicador del indicador.

### Otros datos de la tabla

- **Fecha ing.** = col G "Primer ingreso", al lado de Cat, como AAAAMMDD para que ordene
  sola. Los **Cat P dicen "Proximamente"** en vez de un guion. **Solo 1.745 de 5.527 la
  tienen cargada**: las celdas vacias del Excel llegan como 01/01/1900 y se descartan.
- **V.P. mes** (col CJ) se muestra como referencia. Erik dudo de cambiarla por la venta
  ajustada —que es la que explica el min/max— y decidio **dejar la V.P.**. No reproponerlo.
- **Venta en curso** va **pegada a V.P. mes**, para leer "lo proyectado contra lo real"
  de un vistazo. La V.P. en verde **negrita** y la Venta en curso en verde normal: Erik
  eligio que el peso lo lleve la referencia, no el acumulado.

### La venta perdida y la memoria del mes (17/09)

Erik lo encontro en REDB-111: stock hoy 1, demanda 31, y el dashboard decia que perdia
**31**. La fila se contradecia sola.

- **La cuenta es `demanda - max(venta proyectada, ya vendido + stock hoy)`.** Es la
  formula que planteo el: "si el 1ro habia 30 y hoy hay 28, vendi 2; de los 32 de
  demanda quedan 30 por cubrir y tengo 28, asi que pierdo 2". La proyectada del Excel
  (col CK) sigue entrando por el `max` porque es la unica que contempla **las compras
  que todavia no llegaron**.
- ⚠️ **Por que fallaba:** la proyectada del Excel esta topeada por el stock **al 1ro**,
  no por el de hoy. En REDB-111 al 1ro habia 0 y esa unidad entro despues.

**La memoria del mes** (`aplicar_memoria` en el generador). `stock hoy = stock inicio +
lo que entro - lo que se vendio`: dos incognitas y una ecuacion, asi que con una foto
sola no se puede saber lo vendido, y el Excel **no lo publica** (V.R. mensual llega al
mes cerrado anterior; las columnas VR del mes base estan vacias en las 5.582 filas;
"Dias hab. c/stock" es la ventana de 6 meses, no el mes).

- ⚠️ **La foto anterior ya existe: es el propio `Dashboard_Forecast.html`.** El generador
  se lee a si mismo antes de pisarlo, suma lo que **bajo** desde la corrida anterior y lo
  guarda en el HTML nuevo (campo `VACU`, indice 109). **No agrega ningun archivo al
  circuito.** Si el HTML no esta, arranca de cero y todo se comporta como antes.
- ⚠️ **Solo cuenta las BAJAS, a proposito.** Erik: el stock puede subir por notas de
  credito, devoluciones de clientes o errores de stock. Asi no hace falta saber **por
  que** subio: sube y no pasa nada, baja y eso es venta. Agarra el caso que se perdia,
  el codigo que va 0 -> 1 -> 0 entre el 1ro y hoy.
- Las cinco situaciones estan probadas (`probar_memoria.py`): mismo Excel = no suma nada;
  foto nueva = suma solo las bajas; el stock sube = no resta; **Excel mas viejo = arrastra
  lo acumulado sin volver a contar** (se compara por `stock_iso`, la fecha del stock en
  formato ordenable, porque `stock_ts` es para mostrar y no se puede ordenar); mes nuevo =
  de cero.
- **No recupera el pasado**: empieza a contar desde la primera corrida. El dia que se
  aplico (17/09) el acumulado daba 0 en todos y **no cambio ningun numero** de los 5.527.
- Lo que sigue sin poder verse: lo que entra y sale **dentro de la misma ventana** entre
  dos corridas. Con dos regeneraciones por dia son ~12 hs.
- Diagnostico del dia que sirve de referencia: de 259 codigos cuyo stock subio desde el
  1ro, **144 tenian el ingreso registrado como compra** (ahi la cuenta cerraba sola),
  **97 eran ingresos sin registrar** (710 unidades) y 18 correcciones de stock negativo.
- El generador **saltea la fila separadora** del Excel (codigo "-"): ensuciaba el filtro de
  Categoria con un "-" que no es una categoria. El dashboard paso de 5.528 a 5.527 codigos.

### Decisiones de modelo que Erik ya reviso y cerro (no reproponer)

- El **minimo**: Importados un mes menos, el resto la mitad.
- **Meses por Cat. (col H)** como esta, incluido que en Importados **B y C tengan los mismos
  3 meses** y que en Distribucion haya valores cargados codigo por codigo (A con 1 y 2 m,
  B con 1 / 1,5 / 2 m).

### Pendiente que Erik trajo y no se aplico

Descontar del calculo **lo que ya se vendio del mes** de una forma mas agresiva que la
actual, que bajaria Quiebre de $ 3.833.387 a $ 2.942.726. ⚠️ **No es lo mismo que la
venta perdida de arriba**: esa ya descuenta lo vendido, pero por el `max` con la venta
proyectada del Excel no mueve el Quiebre (ahi `proyectada >= vendido + stock` casi
siempre). Sigue abierto.

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
