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

## Reestructuración del 16/10/2026 — lo que cambió de fondo

Stock del **viernes 16/10 06:33**, 5.384 códigos. Esta vuelta no fue una actualización:
se rehizo buena parte de Estado Stock. **Lo de acá abajo pisa lo que digan las secciones
anteriores.**

### Las solapas se renombraron y se reordenaron

`Forecast · Estado Stock · Histórico Ventas · Proyección Ventas · Acción comercial`.
Acción comercial pasó al final. Los `id` internos (`fc`, `st`, `liq`, `vp`, `hist`) no
cambiaron.

### El Exceso se partió en dos, y el "Indicador Máximo × N" se fue

| | Regla |
|---|---|
| **Exceso leve** | sobre el máximo, hasta el corte elegido |
| **Exceso grave** | por encima de ese corte |

- **El corte lo elige Erik en la barra** (`st.excCut`): *hasta x 1.5 · x 2 · x 3 · x 4*,
  arranca en **1,5**. Mover el desplegable recalcula los estados, la plata de las dos
  tarjetas, el filtro y las cinco solapas. ⚠️ `stkOf` **tira su cache** cuando cambia
  (`_skM`), igual que hacía con el multiplicador viejo.
- Con eso se sacó el indicador **"Máximo × N"**, que era lo que respondía esa pregunta.
  `maxU` ya no lleva multiplicador. Acción comercial conserva el suyo (`st.liq`), que es
  otro control.
- **Los estados son 7, pero las tarjetas siguen siendo 6** porque Rotación se mudó a la
  barra. Mismo encaje de 186px ya medido.
- ⚠️ **La foto mensual sigue guardando 6 estados**, con los dos excesos sumados
  (`FOTO_K` en el generador y `STKH` en la plantilla). Septiembre y octubre están
  congelados con el Exceso entero: partirlo ahora dibujaría en Histórico un salto de 0 a
  1.600 en "grave" que no es movimiento real. **El corte de la foto es fijo en 1,5**
  (`EXC_CUT`): un mes congelado con x2 y el siguiente con x3 no se podrían comparar.
- ⚠️ **El Histórico recorre `STKH`, no `STK`.** Es el bug que esto introdujo y que hubo
  que arreglar: `STK` pasó a 7 estados, el Histórico buscaba la foto de "excleve" y
  "excgrave", que no existen en el JSON, y **el Exceso desaparecía del gráfico y de la
  tabla**.
- Medido el 16/10: el corte no es el problema, el exceso real está muy arriba del máximo
  — **1.034 de 1.875 están en 3× o más**, y 155 tienen máximo 0 (el Excel no les proyecta
  demanda, así que les sobra todo el stock; casi todos reconstruidos).

### La rotación ahora compara VENTA REAL contra VENTA REAL

⚠️ **Este es el cambio más importante y reemplaza todo lo del 15/10.** La tabla de los
cruces tiene 14 columnas en dos bloques:

```
Producto:   Grupo · Código · Cat · Fecha ing.
Stock:      Stock h. · Meses h. · Estado
Histórico:  VR 6 meses · VR 3 meses · Variación · % en stock
Actual:     VR en curso · VD C/C · Avance %
```

- **VR 6 meses = prom(AH, AI, AJ)** y **VR 3 meses = prom(AK, AL, AM)**: dos trimestres
  consecutivos. ⚠️ **"VR 6 meses" NO es el promedio de los últimos seis**, es la mitad de
  atrás de esa ventana. Con los 6 contra los 3, los últimos tres meses estarían de los dos
  lados de la cuenta y amortiguarían la caída.
- **Variación = VR 3 meses / VR 6 meses − 1**, y el umbral arranca en **20%**.
- ⚠️ **No volver a comparar la proyección contra la venta real.** Entre el 15 y el 16/10
  pasó por dos versiones de eso (col BV contra BV del mes anterior, y después VD contra
  el promedio real) y las dos medían si el forecast estaba desalineado, no si el código
  rotaba. MA-0002, con venta real 192, 361, 263, 258, 105, 41, 76, 29, daba **+151% y se
  mostraba "en alza"**; con real contra real da **−77%**, que es lo que muestra la serie.
- **VD volvió a ser la col CJ** en toda la interfaz. Se terminó la excepción de la BV.
- **Se borraron** `DATA.bvant`, `rotacion_prev.json`, `rotVD`, `_BVA`, `rotDelta`,
  `panelRot` y `vbtn`: todo lo que sostenía la cuenta vieja.

### "% en stock": el aviso de que una caída puede ser por faltante

Erik: *"si en mes 6.5.4 tenemos venta prom de 100 y en meses 3.2.1 nos quedamos sin
stock, el promedio va a ser 0, la venta bajó 100%, pero en realidad bajó por falta de
stock"*. Tiene razón y pesa: de 1.108 en baja, **237 tuvieron faltantes** y 498 bajaron
con stock todo el semestre.

- Sale de **la col BS "% días en stock"** (índice **110**), y **BP "Venta con stock"**
  (índice **111**) alimenta el globo: *"61 de 129 días hábiles con stock · vendía 18,6 por
  mes cuando tuvo"*. El caso testigo es **MA-1230006**: −100% con **47% de presencia**.
- ⚠️ **No se puede CORREGIR el número, solo avisar.** BS y BP son un único valor del
  semestre, no hay versión por trimestre, así que no existe "VR 3 meses como si hubiera
  tenido stock". La columna es un semáforo.
- ⚠️ **BS y BP existen SOLO para Importados** (medido: las tienen los 1.778 y ninguno de
  los 3.660 de Distribución y Fabricación). Erik: *"Distribución y Fabricación siempre
  tendrían que tener 100%, porque los fabricamos nosotros o los pedimos y el proveedor
  local te entrega en pocos días"*. Eso vive en `presOf`, que es **regla de interfaz, no
  del dato**.
- ⚠️ **NO usar BT, la "tasa de incertidumbre"** (`=SI(BS<20%;50%;100%)`). Con ese corte
  marca 53 códigos de 5.438 y **5 de los 1.108 en baja**; a MA-1230006, con 47%, le da
  100%. Sirve para lo suyo —castigar el ritmo de un código que casi no existió— no como
  semáforo de faltante.
- **El umbral lo elige Erik** (`st.presU`, 95/90/80/50): por debajo, la Variación se
  pinta **en gris**.
- ⚠️ **Arranca en 50%, no en 90** (Erik, 19/10: *"si su presencia % en stock fue menos de
  50, avisame que la variación puede estar distorsionada, pero si no, ponelo como
  válido"*). Con 90 se apagaban **182** de los 1.115 en baja y avisaba por un 87%, que no
  distorsiona nada; con 50 se apagan **39**, que son los casos de verdad.
- ⚠️ **El 50 se puso acá y no en el Excel: el dashboard NO lee BT**, lee BS directo.
  Cambiar la fórmula de BT (`=SI(BS<20%;50%;100%)`) no movería nada en el dashboard.
  La presencia de los 1.778 Importados, medida el 19/10: **100% en 1.113**, 90-99% en
  185, 75-89% en 177, 50-74% en 138, 20-49% en 112 y menos de 20% en 53.
- ⚠️ **Cada color significa UNA sola cosa** (Erik, 19/10: *"busquemos que el color
  represente lo mismo"*). El primer intento pintaba el % en stock de rojo cuando la
  presencia era baja, y el rojo ya quería decir otra cosa en la Variación de al lado —
  *"cayó de verdad"*. El mismo código mostraba el % en rojo y la Variación en gris, que
  se lee como una contradicción. El reparto quedó así:

  | | |
  |---|---|
  | rojo | cayó · cuesta |
  | verde | subió · vende |
  | **gris** | **sin señal confiable** (la Variación apagada) |

  El **% en stock va siempre neutro**: es el dato de contexto, no la alarma. A los flojos
  los destaca la **negrita**, que no gasta un color. Rige igual por código y por grupo.
- **BR no viaja al HTML**: se deriva, `BR = BS × 129`.

### Rotación y las 6 pastillas no se combinan

⚠️ **"Sin rotación" apaga las pastillas y una pastilla apaga "Sin rotación".** Los dos
vivían en `st.EST`, que filtra por **O**, así que Riesgo + Sin rotación mostraba 173 + 700
= 873 filas como si el cruce hubiera encontrado algo — y es imposible, los estados son
excluyentes. **"En baja" y "En alza" sí se cruzan con las pastillas**: esos son cruces, no
estados, y cruzarlos con Exceso grave es el uso principal.

**"Sin rotación" salió del filtro general de Estado**: se filtra desde el desplegable de
Rotación, que es donde vive.

### Interfaz

- **El "Ver" (Por código / Por grupo) vive dentro del encabezado PRODUCTO**, con la misma
  pastilla amarilla que el par "Proyección / Estado stock" de Histórico, a 16px del
  título. ⚠️ Lleva `text-transform:none` o dice "POR CÓDIGO".
- **Acción comercial congela Grupo, Código y Cat.** (`.acid0/1/2` + la hoja `#acpos`).
  Era la única tabla con scroll lateral que no lo hacía; mide 1.911px contra 1.292.
  ⚠️ Los `left` **no se miden** como en Forecast: `.prevt` es `table-layout:fixed` y el
  colgroup se respeta. Pero tampoco se escriben a mano, porque el ancho del Código es
  dinámico. ⚠️ El título "Producto" se **partió en dos** (colspan 3 fijo + colspan 5 que
  scrollea): una celda con colspan 8 no se congela a medias. ⚠️ El `z-index` de las celdas
  fijas del encabezado necesita **más especificidad** que `.prevt thead tr.h th`, o las
  columnas que scrollean se pintan encima.
- **Fecha ing. 75 → 68px.** Lo que fijaba el ancho no eran las fechas sino
  **"Próximamente"** (73px, 33 códigos Cat P), ahora abreviado a **"Próx."** con el nombre
  completo en el globo. El título "FECHA ING." pide 66, así que 68 es el piso sin tocarlo.

### Las pruebas, otra vez rotas por la forma de la fila

- `probar_estados.py` aprendió los 7 estados y el corte 1,5. **Coincide en los 5.384
  códigos y en los 24 buckets de plata.**
- ⚠️ `probar_memoria.py` usa **`del x[G.VACU:]`, no `del x[G.VACU]`**. Con dos campos
  nuevos después de VACU, borrar uno solo los corre un lugar y `fila(...)[G.VACU]` termina
  leyendo la presencia. **Es la cuarta vez que esta prueba se rompe por depender de la
  forma de la fila y no de la lógica que mide.**
- ⚠️ `chequear_actualizacion.py` **compara solo los campos que tienen las dos versiones**.
  El día que el generador suma un campo, todas las filas quedan distintas y el chequeo
  canta miles de cambios inexistentes: el 16/10 decía *"cambiaron 5.384"* cuando en los
  datos habían cambiado **412**. Es la misma trampa del 24/09, por el otro lado. Ahora
  avisa aparte *"la fila pasó de 110 a 112 campos: el generador cambió, no los datos"*.

### Índices nuevos de `rows[]`

| | |
|---|---|
| 110 | presencia en stock del semestre (col BS) |
| 111 | venta por mes medida solo sobre los días con stock (col BP) |

⚠️ Se agregan **después de `aplicar_memoria`**, que es la que pone VACU (109). Metidos en
`extract` le correrían el índice, que está escrito a mano en la plantilla, el generador y
las dos pruebas.

## Última actualización (14/10/2026)

Stock del **martes 13/10 12:37** (era del 02/10). **5.384 códigos**: salió `BI0906.60N`,
no entró ninguno.

- **La memoria del mes registró 21.740 unidades en 1.143 códigos** desde el 02/10. El
  acumulado de octubre va en **24.049 unidades en 1.266 códigos**.
- El stock se movió fuerte a favor: **Quiebre −113, Riesgo −58, Exceso +142**.
- **3.739 costos cambiaron**, casi todos chicos (mediana 0%, rango −21% a +31%). El
  único salto grande es **HL20-P13W, de USD 0,10 a 8,17**: era uno de los Faros y
  Lámparas cargados a fin de septiembre con costo de relleno, ahora tiene el real.
- Ningún código quedó sin costo. La foto de octubre no se tocó, como corresponde.

## Actualización anterior (02/10/2026) — primer mes nuevo

Stock del **jueves 01/10 06:39**. **5.385 códigos**.

- ⚠️ **Se congeló la foto de OCTUBRE**, la primera que saca el circuito solo. Septiembre
  quedó intacto, como estaba previsto. El Histórico → Estado stock ya tiene **dos meses**
  y los gráficos dibujan línea en vez de un punto.
- La memoria del mes **arrancó de cero**: mes nuevo, es lo esperado.
- El histórico de Proyección sumó **septiembre** (leyó `Forecast 09-26.xlsm`): 8 meses.
  La venta real ya llega a septiembre y pasó de 2.716 a **5.494 códigos**.

| Estado | sep | oct |
|---|---|---|
| Quiebre | 2.477 | 2.393 |
| Riesgo | 226 | 204 |
| Ideal | 251 | 207 |
| Exceso | 1.770 | 1.797 |
| Sin rotación | 744 | 713 |
| Lanzamientos | 58 | 71 |

⚠️ **El primer salto del gráfico de COSTO no se lee como movimiento real.** Exceso pasó
de $ 65,1M a $ 72,2M (+10,9%), y el arreglo de recetas del Gestor ya explicaba +12% por
sí solo (medido el 23/09). La **venta mix sí es limpia**: la perdida de Quiebre + Riesgo
bajó de USD 89.140 a **USD 40.802 (−54%)**. De noviembre en adelante las dos series se
leen derecho.

⚠️ **`probar_memoria.py` ancla su escenario al día 15 del mes** (02/10). Antes salía de
la fecha del stock del día, y con stock del 1/10 la corrida «Excel más viejo» se iba a
septiembre: cambio de mes, la memoria arranca de cero como corresponde, y la prueba
fallaba sin que nada estuviera roto. Es la tercera vez que esta prueba se rompe por
depender del dato del día.

## Actualización anterior (24/09/2026)

Stock del **jueves 24/09 09:16**. **5.385 códigos** (eran 5.372). La memoria del mes
registró **15.995 unidades en 925 códigos** desde el 23/09 06:30.

- **Entraron 13 códigos nuevos** de Faros y barras y Lámparas principales (ECO-*,
  HL20-*, HL40-*, PRO-SQ*), todos **sin Categoría**.
- ⚠️ **Sin Cat ahora es LANZAMIENTO.** Erik, 24/09: *"los sku sin categoría entran en
  Lanzamientos, ahí se guardan los N, P y sin CAT"*. Antes caían en Quiebre, porque no
  son N ni P y tienen stock 0 — un faltante que no existe. Lanzamientos pasó de 58 a 71,
  exactamente esos 13, y son los únicos sin Cat en todo el dashboard. La tarjeta ahora
  cuenta **N · P · s/C**. La regla está en los tres lados: `stkCalc`, `estado_de` y la
  transcripción de `probar_estados.py`.
- **1.006 costos subieron**, todos en pesos, mediana **+12,3%** (de 5,7% a 34,2%).
  Ningún código quedó sin costo.

⚠️ **`chequear_actualizacion.py` comparaba las filas POR POSICIÓN y se corregió el 24/09.**
El día que entran o salen códigos se corre todo lo que viene después y el chequeo cantaba
miles de cambios inexistentes: decía *"cambiaron 3.699 códigos"* cuando en realidad no
había cambiado **ninguno**. Ahora compara **por código** y además informa cuáles entraron
y cuáles salieron.

## Actualización anterior (23/09/2026)

Dashboard regenerado con **stock del lunes 21/09/2026 14:28**: **5.372 códigos**
(eran 5.526). El chequeo previo pasó: el stock avanzó del 17/09 al 21/09.

- **Salieron 154 códigos**, toda la familia `*ESP-FC*` (BESP-FC01…, CESP-FC01…,
  EESP-FC01…). Erik los sacó del Forecast **y** del Gestor a la vez, así que es una baja
  deliberada, no un dato que se perdió. No entró ninguno.
- **La memoria del mes funcionó por primera vez con datos reales**: entre el 17/09 12:35
  y el 21/09 14:28 registró **9.654 unidades vendidas en 910 códigos**. Hasta ahora
  siempre había dado cero porque no había dos fotos que comparar.
- **Los costos se movieron mucho**: de 5.479 códigos comparables, 3.279 quedaron igual,
  2.059 subieron hasta el doble y **41 subieron más de 10 veces**. Esos 41 venían todos
  con el mismo costo de 37,32 — son recetas incompletas que Erik terminó de cargar (ver
  el pendiente de los 1.687). A-109 pasó de 37,32 a 5.167,25. **No es un error de
  lectura**: se verificó columna por columna contra la copia anterior y los códigos que
  Erik no tocó dan idéntico.
- Ningún código quedó sin costo.

⚠️ **Cambió la forma de bajar el Gestor de precios.** El export a xlsx del conector de
Drive dejó de funcionar (*«File too large for export»*, el Sheet pesa 4 MB). Ahora se baja
como **CSV**, que trae solo la primera hoja —que es `General`, la única que se usa— y se
rearma el xlsx. El detalle está en la skill `forecast-dashboard`. **Verificar el
encabezado antes de regenerar**: el generador lee por posición de columna.

### La foto mensual del estado de stock (18/09)

`foto_mensual()` en el generador guarda, en `scripts/historico_stock.json`, el reparto de
los 6 estados **por grupo** y el estado de **cada código** (una letra).

- ⚠️ **La foto se saca en la PRIMERA corrida del mes y no se toca nunca más.** Erik:
  *"si el 2 de octubre cambia algo no importa, ya tenemos la foto del 1/10"*. Es una foto
  de inicio de mes, no un cierre.
- **Septiembre quedó congelado el 18/09** con el stock del 17/09 12:35, desde el dashboard
  que estaba publicado (`scripts/congelar_septiembre.py`, que existe solo para esa vez).
- Al HTML viaja **solo el total por grupo** (`solo_ga`). El detalle por código se guarda
  pero no se publica: son 5,4 KB por mes que hoy nadie lee, y si no se guardaran, el mes
  se cerraría sin ellos y no habría forma de recuperarlos.
- **Cada estado guarda además su plata**: `c` y `m`, abiertos por moneda. ⚠️ **No son el
  valor del stock: son los dos montos que muestra su tarjeta en Estado Stock**, y el
  significado cambia según el estado (costo a invertir / inmovilizado / parado, y la venta
  mix perdida / inmovilizada / parada). La cuenta vive en `plata_de()`, copiada de `CARDS`.
- ⚠️ La regla de los 6 estados está escrita **dos veces** — `stkCalc` en la plantilla y
  `estado_de` en el generador — y desde el 23/09 **la plata también** (`plata_de` contra
  `CARDS`). No hay forma de evitarlo: la foto se calcula antes de armar el HTML.
  **`scripts/probar_estados.py` es el seguro** y ahora compara las dos cosas: correrlo
  después de tocar cualquier cosa de los estados **o de la plata de las tarjetas**. El
  23/09 coinciden en los 5.372 códigos y en los 20 buckets de plata.
- **Septiembre se rearmó el 23/09 para sumarle la plata** (`scripts/congelar_mes.py`),
  desde el dashboard del commit `caeae9e`, que es exactamente el del stock 17/09 12:35.
  No es reescribir la historia: es la misma foto con los campos que faltaban, y los SKU
  por estado dieron idénticos. Verificación fuerte: la venta mix perdida de Quiebre +
  Riesgo dio **USD 89.140**, el mismo número que ya estaba medido.
  - ⚠️ **La plata de septiembre usa los costos de septiembre**, como corresponde a una
    foto. Eso significa que el primer salto sep → oct en el gráfico de **costo** va a
    incluir el arreglo de recetas del Gestor, no solo movimiento real: medido, Exceso en
    pesos +12%, Riesgo +18%, Quiebre −35%, Sin rotación +8%. En **USD es +1%** y **la
    venta mix no se mueve nada** (el mix es precio de venta, no costo), así que ese
    gráfico se lee limpio desde septiembre.

### La solapa Histórico, las dos historias (23/09)

El selector de la esquina alterna **Proyección** (VP contra VR, la de siempre) y
**Estado stock** (la foto mensual de los 6 estados).

- **Dos gráficos de líneas, lado a lado**: SKU a la izquierda, plata a la derecha.
  ⚠️ **Lado a lado y no apilados**: en vertical eran 500px de gráficos antes del primer
  número de la tabla. El de plata elige **Costo / Venta mix** y **$ / USD** — el dashboard
  nunca suma pesos con dólares, así que un solo eje con las dos monedas sería mentira.
  - ⚠️ El reparto es muy disparejo (Quiebre 2.477 contra Lanzamientos 58; en plata el
    Exceso se come el eje). **La referencia es clickeable**: apagar un estado reacomoda el
    eje. Es la única forma de mirar los chicos.
  - Usan **todos los meses guardados**, no los 3 de la tabla: la tabla es para leer el
    número y el gráfico para ver la forma.
- **La tabla agrupa de dos maneras, a elección** (`st.histGrupo`). Erik: *"mi única duda
  es si agrupar los estados y de esa forma veo en la tabla los quiebres uno al lado del
  otro"*. Es la misma data ordenada distinto, así que en vez de elegir por él quedó el
  botón: **Por mes** (como Proyección) y **Por estado** (los quiebres pegados).
- **Tres meses a la vez.** Con 6 sub-columnas por mes, cuatro dan 1.494px contra los 1.307
  útiles y vuelve el scroll lateral. Con tres da 1.253 y entra entero.
- ⚠️ **Los seis títulos van con el color de su estado y los valores todos iguales.** Erik:
  el amarillo del Exceso sobre fondo blanco no se leía. Y sobre el azul del encabezado hay
  que **aclarar** los colores (`HSTK_C`) o el verde del Ideal y el azul de Lanzamientos
  desaparecen; como línea sobre blanco, el Exceso va en ámbar (`HSTK_L`).
- ⚠️ **El `top` pegajoso de la segunda fila se MIDE** (`fijarR2`), no se escribe a mano.
  Escrito a mano ya se desincronizó dos veces del alto real de la primera fila y el
  síntoma es feo: queda un hueco por el que pasan las filas del cuerpo al scrollear.
  Las tres tablas de Proyección e Histórico van al **mismo alto de encabezado, 110px**:
  antes saltaba de 106 a 75 al alternar las vistas.
- ⚠️ La vista responde a los filtros de **Unidad de negocio y Grupo solamente**. Categoría,
  Código y Estado necesitan el detalle por código, que se guarda en el JSON pero no viaja
  al HTML.

## Estado anterior (14/09/2026)

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
- ⚠️ **El Faltante DESCUENTA la compra del mes** (18/09): `max(0, maximo - stock -
  compra)`. Responde "cuanto tengo que comprar", asi que no puede pedir de nuevo lo que
  ya esta en camino. Erik lo vio en PRO-T11-39-B: decia "Faltante 456 · USD 390" con
  **800 unidades ya compradas**. *"No tendria que decir faltante"*.
  - Medido: de 2.703 codigos en Quiebre o Riesgo, **1.453 tienen compra en camino y
    1.413 ya estan cubiertos del todo** -- el 52%. El "Costo a invertir" de las tarjetas
    bajo de USD 323.552 / $ 12.067.465 a **USD 253.179 / $ 8.716.105**: USD 70.373 que
    ya estaban gastados y el dashboard volvia a pedir.
  - La columna **Compra** va en el bloque Faltante, antes de las unidades, para que la
    fila se lea sola: *viene esto, falta esto, cuesta esto*. Sin ella, un Quiebre con
    faltante "-" parece un error. El globo agrega "Para el maximo faltan 456 · ya
    vienen 800".
  - ⚠️ La venta perdida **ya contemplaba la compra** por el tope con la col CK: era el
    otro lado de la misma moneda. No se toco.
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
| **Lanzamientos** | Cat **N, P o sin Cat**, sin importar el stock | azul |
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

### Quiebre y Riesgo "con ingreso" (15/10)

Erik lo vio en Lámparas auxiliares: 12 códigos en Quiebre, todos con compra de 400 u 800
unidades y faltante "–". La fila era correcta —Quiebre es el stock de **hoy** y la compra
es lo que entra **este mes**— pero a simple vista parecían el mismo problema que un
quiebre sin nada en camino. Él: *"se podría marcar el estado como Quiebre con ingreso y
que tenga otro color"*, y enseguida *"seguramente pase lo mismo en riesgo"*. Tenía razón.

- ⚠️ **NO son estados nuevos: es una marca dentro del estado.** El código sigue contando
  como Quiebre o Riesgo en la tarjeta, en el filtro y en la foto mensual; lo único que
  cambia es la pastilla. **Un séptimo y octavo estado romperían dos cosas ya pedidas**:
  que los 6 sean excluyentes y sumen 100%, y que las 6 tarjetas entren en un renglón en
  la notebook.
- Medido el 15/10: **Quiebre 91 de 2.319 (4%)**, 68 ya cubiertos hasta el máximo;
  **Riesgo 75 de 161 (47%)**, 31 cubiertos. En Riesgo es casi la mitad del estado.
- ⚠️ **El color es el del estado pero EN CLARO, con la letra oscura**
  (`.st-p-cero-ing` #ffcdd2/#b71c1c, `.st-p-riesgo-ing` #ffe0b2/#e65100). Erik pidió
  *"rojo pero más claro"*: un rojo claro con letra blanca es ilegible en una pastilla de
  0,6rem. Fondo claro con letra oscura se lee, y ya es patrón del dashboard (Exceso es
  amarillo con letra roja).
- La tarjeta agrega **"N c/ing."** al lado del conteo. La pastilla mide 92px, igual que
  las otras: **la tabla no se ensanchó** (1.266px, los mismos que antes).

## La tarjeta Rotación y los dos cruces (15/10)

La sexta tarjeta de Estado Stock dejó de llamarse "Sin rotación" y pasó a ser
**Rotación**, con un desplegable de tres sub-estados: **Sin rotación · En baja · En alza**.

### De dónde sale el dato

⚠️ **Compara la col BV "Venta ajustada" del Forecast de hoy contra la del Forecast
congelado del mes anterior** (`Histórico\Forecast MM-AA.xlsm`). Es el ritmo mensual con
el que el Excel calcula "Meses actual": la misma base del mínimo, el máximo y los 6
estados. Si ese ritmo se mueve, se mueve todo el modelo.

  Verificado con el ejemplo de Erik — **MA-0002: septiembre 180, octubre 122, −32%**.

⚠️ **OJO CON EL NOMBRE.** Erik la llamó "VD", pero en el dashboard **VD es la col CJ**:
son columnas distintas. Por eso en la interfaz esto se llama *rotación* y nunca VD.

- Lo lee `rotacion_anterior()` en el generador, que cachea el ritmo anterior en
  `scripts/rotacion_prev.json` y **solo relee el Excel cuando cambia el mes** (pesa 19 MB).
- Viaja al HTML como `DATA.bvant`, **una lista alineada con `rows[]`**: 25 KB contra los
  100 KB que costaría un `{código: valor}`.
- Los dos nombres de columna (Septiembre / Octubre) **salen solos**: el izquierdo de
  `DATA.bvant_mes` y el derecho de `DATA.months[0]`. En noviembre dicen Octubre y
  Noviembre sin tocar nada.

### Qué son y qué NO son los sub-estados

- ⚠️ **"Sin rotación" sigue siendo uno de los 6 estados excluyentes.** Sacarlo del modelo
  devolvería **683 de sus 709 códigos al Exceso** (sin ventas → ritmo 0 → máximo 0 →
  Exceso por definición): es el problema de los $ 35 millones que se arregló el 16/09.
- ⚠️ **"En baja" y "En alza" son CRUCES, no estados.** Con umbral 30%, los 92 que cayeron
  están repartidos en Exceso, Quiebre, Riesgo y Lanzamientos. **Por eso la tarjeta no
  muestra % sobre el total**: dejó de ser una porción. Lo pidió Erik por intuición y los
  números le dieron la razón.
- ⚠️ **Los tres son excluyentes entre sí** (un desplegable, no tres botones), pero **no
  tocan el filtro de las otras cinco tarjetas**: cruzar "En baja" con "Exceso" es el uso
  principal — *de mi sobrante, cuál encima se está cayendo*.
- ⚠️ **Los Sin rotación quedan AFUERA de los dos cruces.** Erik encontró 2 en "En baja":
  su caída ya está contada en el primer sub-estado.
- Los que **arrancaron de cero** (ritmo anterior 0 y hoy > 0) cuentan como alza y la tabla
  los muestra como "nuevo". ⚠️ Al ordenar por Rot. % van **al fondo**: no son un
  porcentaje y arriba tapaban los aumentos reales.

Medido el 15/10 con 5.384 códigos: **2.420 comparables**, 2.932 sin ritmo anterior.

| Umbral | En baja | En alza |
|---|---|---|
| 10% | 426 | 468 |
| 20% | 183 | 285 |
| 30% | 92 | 213 |

### La plata: solo en Sin rotación

⚠️ **Los dos cruces NO muestran plata, y es una decisión cerrada.** Pasó por tres
versiones antes de llegar acá, así que no volver a empezar:

1. Primero era **stock × costo**. No servía: en una baja no importa el stock entero.
2. Después **la caída × costo** (Dif. cant. × costo unitario), la cuenta que pidió Erik
   con MA-0002: 58 unidades × USD 29,7697 = **USD 1.726,64**.
3. Al final la sacó: *"en baja y en alza no quiero ver nada de costo y venta, es al pedo"*.
   **Y tiene razón**: obligaba a inventar qué significaba —"inmovilizado" en una baja, "a
   invertir" en una alza— y ninguna era una decisión de compra. Esa sale del estado del
   código, que ya tiene su tarjeta con su plata. Acá importa *qué se movió y cuánto*.

**Sin rotación sí la conserva** (`Costo inmovilizado` / `Venta mix inmovilizado`, stock ×
costo y stock × mix): ahí no es un invento, es el stock entero parado. ⚠️ Ese nombre
reemplaza al "Costo parado / Venta mix parado" que tenía cuando era tarjeta propia.

### La tabla propia de los cruces

Erik: *"no veo utilizable el diseño de tabla que tenemos para el resto de los estados en
este caso"*. Los cruces tienen la suya, de **13 columnas y 941px**; Sin rotación usa la de
siempre porque es un estado normal.

```
Producto: Grupo · Código · Cat · Fecha ing. · VD · VC
Stock:    Stock h. · Meses h. · Estado
Rotación: Septiembre · Octubre · Rot. % · Dif. cant.
```

- Ordena con la regla de siempre: un clic de mayor a menor, el segundo vuelve al orden de
  arranque (por cuánto se movió el ritmo).
- **Tiene las dos vistas, Por código y Por grupo.** ⚠️ Al principio no: con un cruce
  activo se dibujaba la tabla sin mirar `VIS` y el botón "Ver" quedaba de adorno. Erik lo
  encontró. La vista por grupo reusa `st.gaOpen` y `tglGA`, igual que la tabla de siempre.
- ⚠️ **El Rot. % de un grupo NO es el promedio de los de sus códigos**: sale de los
  totales, `suma(hoy) / suma(anterior) − 1`. Promediar porcentajes le daría el mismo peso
  a un código que mueve 2 unidades que a uno que mueve 900.
- ⚠️ **La columna Cat necesita 46px**, igual que en la tabla principal: la pastilla mide
  41 y con 33 recortaba. Es el mismo valor que ya estaba documentado y se volvió a pisar.

### El encaje de las seis tarjetas, que costó

⚠️ **Las cinco tarjetas de hoy ya ocupaban los 1.221px justos** (5 × 237 + 4 × 9). Meter
una sexta obligó a tres cosas, todas medidas:

1. El **ancho mínimo** bajó de 200 a **186px**: con 200, seis piden 1.245.
2. El **subtítulo bajó a su propia línea** y el `c/ing.` a la de abajo, porque la línea del
   título pedía 226px y quedan 172 útiles. Erik eligió ese reacomodo.
3. El **renglón de `c/ing.` se reserva en las seis** (con un espacio cuando no hay), o
   Quiebre y Riesgo quedan con una línea más y su separador cae 13px más abajo.
   ⚠️ Se probó empujar la plata al pie con `margin-top:auto` y **es peor**: alinea el
   fondo, no el separador, porque los importes ocupan una o dos líneas según el código
   tenga una moneda o dos.

Resultado: **las seis en un renglón, 172px de alto, separadores a la misma altura.**

⚠️ **La tarjeta de Rotación usa el MISMO contenedor que las otras cinco** (no
`class="card"`, que es otra cosa): mismo borde, radio, sombra y relleno `11px 12px`. Con
otro contenedor las pastillas no arrancan a la misma altura. Lo único distinto es el
fondo **#dde2f0**, elegido con distancia contra el blanco de las otras **y** contra el
gris de la página (#eef0f8): con un tono más suave se perdía en algunos monitores.
Su pastilla es la única sin `min-width:112px` — 112 + 6 + 84 del desplegable dan 202 y
hay 172.

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
- ⚠️ **`probar_memoria.py` ARMA su escenario, no lo toma del dashboard del dia.** Daba por
  sentado que REDB-111 tenia stock 1 y acumulado 0 — cierto el 17/09, falso el 23/09 en
  cuanto la memoria empezo a acumular de verdad, y la prueba fallaba sin que nada
  estuviera roto. Es la misma trampa que las fechas escritas a mano. **Ningun valor del
  dia puede quedar clavado en la prueba.**
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

### Los 100 codigos con "ingresos sin registrar": CERRADO (17/09)

Se detectaron 100 codigos cuyo stock subio desde el 1ro sin una compra que lo explicara
(910 unidades). **Erik: era un recuento de inventario.** El stock actualizado es el
bueno y no hay nada que corregir en el Excel. No volver a levantarlo como problema.

⚠️ Lo que si conviene tener presente: la memoria del mes **cuenta las bajas de stock como
venta**. Un ajuste de inventario que suba el stock no molesta -- solo se cuentan las
bajas -- pero uno que lo **baje** se va a contar como venta, y desde el stock solo no hay
forma de distinguirlos.

### Descontar lo vendido de forma mas agresiva: CERRADO (18/09)

**No se hace. Erik lo cerro el 18/09 despues de ver los numeros. No reproponerlo.**

La idea era sacar el tope con la venta proyectada del Excel. Una nota vieja decia que
bajaria el Quiebre de $ 3.833.387 a $ 2.942.726, pero esa nota era de **antes** de la
venta perdida que se aplico el 17/09. Medido sobre el modelo actual, el efecto es el
contrario:

| | Venta mix perdida (Quiebre + Riesgo) |
|---|---|
| Como esta hoy | USD 89.140 · $ 4.999.628 |
| Sin el tope | USD 114.466 · $ 9.784.119 |

⚠️ **El tope ES la compra del mes.** La col CK del Excel vale
`min(demanda, stock al 1ro + compras del mes)`, asi que sacarlo seria ignorar la
mercaderia ya comprada y en camino. Erik: *"para mi el ingreso hay que tenerlo en
cuenta, o sea la compra del mes en cuestion"*.

De los 110 codigos que cambiarian, **77 tienen compra en camino**. Ejemplo:
PRO-T11-39-B tiene demanda 160, stock -1 y **compra de 800**; hoy marca perdida 0, que
es lo correcto, y sin el tope marcaria 161. Los 33 sin compra tampoco mejoran: ASX11
pasaria de 1.316 a 1.416 porque se sumaria el stock negativo como demanda extra.

**Lo que Erik queria -- descontar lo ya vendido -- ya funciona** desde el 17/09: es la
columna VC y la cuenta `demanda - max(venta proyectada, ya vendido + stock hoy)`.

## Datos del Excel que conviene mirar
- [x] **Venta ajustada negativa: CORREGIDO por Erik el 17/09.** Eran 6 códigos con más
  devoluciones que ventas (IB2810.40, IMI2509.10, IV2313.10, RV099.30, BB1010.30,
  BDE0906.30) que daban meses de cobertura absurdos, hasta −108. Hoy los seis quedaron
  en 0 y **no hay ninguno negativo en los 5.526**.
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

## Interfaz homogénea en las cinco solapas (17/09, tarde)

Erik: *"tratemos de que en todas las solapas, filtros, opciones, detalles, estética,
títulos, todo eso vaya siendo homogéneo, sino cada hoja es un mundo distinto de uso"*.
Se auditaron las cinco midiendo en el navegador y se unificaron. **No volver a que cada
solapa tenga lo suyo.**

### Un solo tamaño

Antes convivían tres: Proyección e Histórico eran **22% más grandes** que el resto.
Ahora las cinco van a **letra 12px en el cuerpo, 10px en el encabezado y 28px de fila**.

- ⚠️ El alto lo manda **la pastilla de Cat/Estado (17px)**, no el texto. Con 6px de
  padding la fila daba 30; con 5px y `line-height:15px` cierra en 28.
- ⚠️ Los tamaños están en **varios lugares que se pisan**: `table`, `.prevt`, `.vptable`,
  `.r1 th`, `.r2 th`, `.vptable thead th`, `.vpid`, y **dos estilos en línea** (la
  constante `TH` y el generador `GH` de Estado Stock), que le ganan al CSS. Cambiar uno
  solo no alcanza.

### Sin scroll lateral en notebook

Erik: *"necesito ver todas las columnas juntas, no me gusta el scroll lateral"*. La
tabla de Estado Stock pasó de 1.439 a **1.248px declarados**, contra los **1.292
disponibles** a 1.366 de pantalla.

- ⚠️ **Cuando aparece la barra vertical el espacio baja de 1.322 a 1.292.** Hay que
  apuntar al número chico o vuelve el scroll.
- Lo que se recortó: los **paréntesis de los títulos de grupo** ("FALTANTE (para llegar
  al stock máximo)" obligaba a 202px entre dos columnas cuando los datos pedían 152),
  los títulos largos (**Stock h.**, **Meses h.**, **Unid.**) y el **espacio interno de
  las celdas de 8 a 6px**, que son 4px × 18 columnas = 72px y no se nota.
- Todo lo que se acortó **lleva el nombre completo en el globo**.

### Encabezados más bajos

Cada barra sobre las tablas gastaba un renglón. Se metieron adentro del encabezado:

- **Forecast**: el mes y su selector "Stock mín" pasaron a un solo renglón (48 → 30px), y
  las flechas de mes están dentro del panel "Stock al …".
- **Proyección e Histórico**: las flechas y el botón **Generar Excel** están dentro de la
  celda "Grupo de artículo". El bloque alto bajó de 126 a **104px** (su contenido usa 98).
- ⚠️ **Los `top` pegajosos van atados a esos altos** (`.r2 th{top:}` y
  `.vptable thead tr.r2b th{top:}`). Si se cambia un alto sin mover su `top`, las dos
  filas de encabezado **se superponen**.

### Ordenar: una sola regla

⚠️ **El orden de arranque es UNO SOLO, `porCodigo()` (24/09): grupo con la prioridad de
los filtros, después código en orden NATURAL** (`localeCompare('es',{numeric:true})`).
Antes cada tabla tenía el suyo — Forecast alfabético puro, Acción comercial el orden crudo
del Excel sin agrupar, Estado Stock ya el natural. Erik lo encontró filtrando Exceso:
Estado Stock y Acción comercial mostraban **listas distintas**. Eran los mismos 1.751
códigos, pero ordenados distinto, y **como cada tabla corta en 500 la primera página no
coincidía**. En alfabético puro MA-10461025 cae entre MA-0037 y MA-3023: son 370 códigos
con números largos metiéndose en el medio. Arrastra el CSV del Forecast y el Excel de
Acción comercial, que siguen a su tabla. **Proyección e Histórico no se tocan.**

**Un clic ordena de mayor a menor. El segundo vuelve al orden por código.** Sin flechas
ni símbolos: el globo dice "clic para ordenar". Rige en Forecast, Estado Stock y Acción
comercial.

- ⚠️ **Forecast tenía `setSort` y `sortRows` escritos pero ningún `onclick` los llamaba**:
  era código muerto. Se conectaron el 17/09.
- **Grupo no ordena** (Erik: de las de texto, solo Código). Clickearlo nunca ordenó
  alfabéticamente, usaba la prioridad de los filtros.
- ⚠️ **Proyección e Histórico NO ordenan, y queda así. Erik lo cerró el 17/09: "dejalo
  como está ahora". No reproponerlo.** Sus filas son totales por grupo partidos en dos
  segmentos (IMPORTADOS y DISTRIB./RECONSTR.) con su propia fila de TOTAL: un orden
  global los mezclaría, y hacerlo por segmento obligaba a elegir cuál de las seis
  columnas de cada mes manda. No le hace falta.

### Un solo pie

Las tres tablas que cortan dicen **"Mostrando 500 de N · ver 500 más"**. Acción comercial
agrega *(los totales suman todos)*, que es cierto y no se puede perder.

- ⚠️ **El tope crece de a 500, nunca de golpe.** Un "ver todo" volvía a pagar el segundo
  y medio entero. Medido: 203 filas 53ms, 1.796 filas 173ms, **5.527 filas 1.467ms** — no
  escala, porque el navegador calcula la posición de ~100.000 celdas.
- El tope **se reinicia al cambiar un filtro**, para no quedar en modo lento sin darse
  cuenta. Y **el orden se aplica antes del corte**, así que arriba queda lo que se busca.

### Vocabulario de las ventas

**VD** venta demanda (col CJ) · **VP** venta proyectada (col CK) · **VR** venta real ·
**VC** venta en curso. Erik lo encontró en MA-0040, que mostraba "VP 29" en Forecast y
"V.P. mes 33" en Estado Stock: eran dos columnas distintas del Excel llamadas igual.

- El bloque verde de Estado Stock se llama **"Venta perdida"** (era "V.P. mensual
  perdida", que además estaba mal: lo que se pierde es demanda).
- ⚠️ El Excel de Proyección arma sus encabezados **aparte** (`rSub`): hay que cambiarlo
  ahí también o el archivo exportado queda con el vocabulario viejo.

### Los globos

El `title` nativo lo dibuja el sistema operativo y **no se puede pintar**. Hay un tooltip
propio (`#tip`), uno solo colgado del `body`: `data-tip` es el nombre (blanco) y
`data-tip2` la ayuda de uso (amarillo). Va en el body y no dentro del `th` porque las
tablas tienen `overflow:hidden` y se lo comerían.

### Los nombres de grupo, abreviados

`Portaescobillas de alternador` → **PE alternador**, `Portaescobillas de arranque` →
**PE arranque** (`GAABR`/`gaLbl`). ⚠️ Es **solo para mostrar**: `DATA.GA` conserva el
nombre completo, así que el orden, los filtros, las claves de agrupación y lo que sale en
el Excel y el CSV no cambian. Eso solo sacó las dos líneas de la columna Grupo.

### Lo que se borró por obsoleto (17/09)

Erik: *"todo lo que esté obsoleto borralo"*. Se sacó solo lo que **no llamaba nadie**,
verificado contando usos en toda la plantilla (definición + llamadas = 1 significa que
la única aparición es la propia definición):

- `renderLiqTable` — la versión vieja de la tabla de Acción comercial, apuntaba a un
  `tablaLiq` que no existe en el HTML.
- `sortRed` — ordenaba "primero los que están en rojo". Nunca se conectó.
- `ar(k)` — dibujaba la flecha ▲▼ del orden. Con el orden siempre de mayor a menor no
  hay dirección que mostrar.
- `exportPNG` **y la librería html2canvas**. El botón se sacó el 14/09 y quedaron los
  dos. Las dependencias externas pasaron de 3 a 2.
- Los estilos `.mpager` y `.ar`, de cosas que ya no existen.
- **El punto verde** al lado del código: decía lo mismo que la columna VC. El dato
  `movio` sigue, porque es lo que decide si un código puede llamarse "sin rotación".

⚠️ **Chart.js y XLSX SÍ se usan** — los Excel y las tortas del resumen — y no se tocan.
Dicho eso, no se logró que las tortas se dibujaran ni en el productivo ni en el preview
(cero `<canvas>` en los dos): puede ser otro resto muerto, pero **no se borró sin poder
confirmarlo**.

### Trampas del código que costaron encontrarse

- ⚠️ **`tablaLiqPrev` es la tabla VIVA de Acción comercial.** La muerta es
  `renderLiqTable` / `tablaLiq`, que apunta a un elemento que no existe. Es fácil
  confundirlas y borrar la que anda.
- ⚠️ Acción comercial **ya cortaba en 500** por su cuenta (`_capP`). El `const cap=3000`
  que se ve cerca está en el código muerto.
- ⚠️ La vista por grupo de Estado Stock se llama **`'ga'`, no `'grp'`**. Medirla mal
  devuelve los mismos números que la de código y no se nota.
- ⚠️ **Medir o verificar anchos SIN levantar el tope de 500 filas mide solo esas 500**, y
  los valores más anchos están más abajo. Hay que poner `st.tope={st:DATA.rows.length}`
  y volver a dibujar **antes** de medir y antes de verificar. Paso el 18/09: daba cero
  cortes y en realidad había 100. También aplica al chequeo de filas partidas en dos.
- ⚠️ En la plantilla **los acentos conviven en dos formas**: como carácter (`á`) y como
  escape literal (`á`). Un anclaje que no use la forma correcta no engancha.

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
