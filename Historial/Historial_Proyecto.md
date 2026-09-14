# Historial del Proyecto — Dashboard Forecast (Electroestrada)

Cómo se llegó hasta acá y por qué. **Leerlo antes de cambiar una regla de negocio**:
mucho de lo que parece un detalle arbitrario se decidió por algo. El estado actual, en
cambio, está en `CLAUDE.md` (en la raíz de la carpeta).

## La etapa Cowork (jul–sep 2026) y la mudanza a Claude Code

El dashboard se construyó entero en Cowork. El **14/09/2026** dejó de poder usarse: una
actualización de Windows del 08/09 bloquea el acceso de ese entorno a los archivos de la
PC. **Claude Code no está afectado** — lee los Excel de Drive (`G:`) sin problema — así que
el proyecto se mudó acá. (Pasó exactamente lo mismo con el dashboard del Taller BV.)

Ese día también se ordenó la carpeta: el generador pasó a `scripts/`, las skills a
`.claude/skills/` (se cargan solas), la documentación a `Historial/`, y se sumó el chequeo
previo a publicar (`scripts/chequear_actualizacion.py`), que nació justamente del problema
descrito abajo en "Fecha del stock".

## Fecha del stock: por qué se chequea antes de publicar

El 14/09/2026, al regenerar, el dashboard salió con **stock del viernes 04/09** cuando lo
publicado tenía **stock del lunes 07/09**: el dato iba para atrás. La fecha sale de las
celdas **BN2 / BO2** de la hoja Forecast ("Base SAP" + hora), y había quedado vieja.

Se detectó a tiempo y no se publicó. Para que no dependa de que alguien se dé cuenta, el
`.bat` ahora compara la fecha del stock nuevo contra la del publicado y **frena pidiendo
confirmación** si va para atrás.

---

# Memoria de trabajo — último chat de Cowork (14/09/2026)

> Dos temas grandes:
> (1) migración de la Venta real a "V.R. mensual" con 3 columnas, y
> (2) arreglo + análisis de la fórmula "Meses fin de mes" (caso MA-0040).

---

## 1) Venta real → hoja "V.R. mensual" con 3 columnas (HECHO)

**Qué se cambió y por qué.** La venta real (unidades + importes) ahora se lee de
**V.R. mensual**, que pasó a tener **3 columnas por mes: Cantidad / Pesos / Dólares**
(antes las unidades salían de la hoja "24-25-26", ya borrada). Además la V.R. mensual
dejó de ser un archivo suelto y ahora vive como **hoja dentro de `Forecast.xlsm`**.

**Layout de la hoja** (confirmado con foto de Erik): fila 1 = nombre del mes (Feb 2026 …
Ago 2026), fila 2 = subencabezados `Cantidad` / `Pesos` / `Dólares`, código en columna C.
Cada mes son 3 columnas; el `$` y el `USD` de las celdas son formato, no columnas extra.

**Cambios en `generador/generar_dashboard.py`:**
- `read_realusd(folder, forecast_path=None)`: primero busca una hoja llamada
  `V.R. mensual` / `Venta real` / `VR` dentro de `Forecast.xlsm`; si no está, cae al
  archivo suelto como respaldo. Devuelve `{codigo: {mes: [cant, pesos, dolares]}}`.
- `_parse_realusd_rows(rr, origen)`: parser común (detecta mes en fila 1, subcolumnas en
  fila 2). **Normaliza tildes** (ó→o, etc.) para que reconozca el encabezado "Dólares".
- Histórico: V.R. unidades = `cant`; V.R. $-USD = **Dólares si el código es Importado,
  Pesos si es Nacional** (misma lógica de moneda del dashboard). Se arma
  `imp_cods = {códigos con UN == "Importados"}` y se pasa a `build_historico(..., imp_cods)`.
- El dashboard **no cambió**: sigue mostrando una sola columna V.R. $-USD (importados en
  dólares, nacionales en pesos). El generador solo elige la columna de moneda según el UN.

**Estado:** el `.bat` corrió OK el 02/09 leyendo `hoja 'Venta real' de Forecast.xlsm ->
2716 códigos, meses [2..8] (cant/pesos/dolares)`. Erik iba a **renombrar la hoja a
"V.R. mensual"** (el generador la reconoce igual) y **borrar el archivo suelto**.

---

## 2) Fórmula "Meses fin de mes" — bug y arreglo (caso MA-0040)

### El problema
La columna **"Meses fin de mes"** (ej. CQ para septiembre) mostraba **1.1 meses con stock
final 0**. Fórmula original:

```
=SI.ERROR((CO12+CT12)/((CK12+CY12+DM12+EA12+EO12+FC12)/((CK12>0)+(CY12>0)+(DM12>0)+(EA12>0)+(EO12>0)+(FC12>0)));0)
```

El numerador `(CO12+CT12)` = **Stock inicio + Compra** = lo disponible al *arrancar* el mes.
**Nunca resta la venta**, así que, pese al nombre "fin de mes", muestra la cobertura de
arranque → por eso stock 0 pero 1.1 (y ese 1.1 se arrastraba al mes siguiente).

### El arreglo (DECIDIDO)
Cambiar el numerador a **stock final = Stock inicio + Compra − Venta proyectada** = `CO+CT−CK`.
Erik anula el stock negativo por otro lado, así que **va sin `MAX`**. Fórmula final
(español, separador `;`):

```
=SI.ERROR((CO12+CT12-CK12)/((CK12+CY12+DM12+EA12+EO12+FC12)/((CK12>0)+(CY12>0)+(DM12>0)+(EA12>0)+(EO12>0)+(FC12>0)));0)
```

MA-0040 septiembre: `(29+0−29)` = 0 → **Meses = 0.0** ✓ (antes 1.1). Ritmo (denominador)
sin tocar = 27.2.

### El denominador NO se toca (decisión de Erik)
El ritmo es el **promedio de la Venta proyectada de 6 meses hacia adelante (actual + 5),
ignorando los meses en 0** (`suma / conteo(>0)`). Se evaluó simplificarlo con
`PROMEDIO.SI` sobre el rango contiguo `AU:BH`, pero **Erik lo descartó**: `AU:BH` es la
*demanda* cruda; si un mes futuro no va a tener stock, la venta real es 0 y hay que
reflejarlo. Usar la demanda daría un "consumo mentiroso". Por eso se queda con
`CK,CY,DM,EA,EO,FC` (Venta proyectada topeada por stock), que **no son contiguas**
(cada 14 columnas) → no se puede acortar.

### Cómo se replica en los 12 meses
Cada bloque mensual tiene su columna de Meses. Solo cambia el **numerador** por
`(StockIni + Compra − VP)` de ese bloque (denominador de cada mes queda como está):

| Mes | Col. Meses | StockIni | Compra | VP | Numerador |
|---|---|---|---|---|---|
| Sept | CQ | CO | CT | CK | `CO12+CT12-CK12` |
| Oct | DE | DC | DH | CY | `DC12+DH12-CY12` |
| Nov | DS | DQ | DV | DM | `DQ12+DV12-DM12` |
| Dic | EG | EE | EJ | EA | `EE12+EJ12-EA12` |
| Ene | EU | ES | EX | EO | `ES12+EX12-EO12` |
| Feb | FI | FG | FL | FC | `FG12+FL12-FC12` |
| Mar | FW | FU | FZ | FQ | `FU12+FZ12-FQ12` |
| Abr | GK | GI | GN | GE | `GI12+GN12-GE12` |
| May | GY | GW | HB | GS | `GW12+HB12-GS12` |
| Jun | HM | HK | HP | HG | `HK12+HP12-HG12` |
| Jul | IA | HY | ID | HU | `HY12+ID12-HU12` |
| Ago | IO | IM | IR | II | `IM12+IR12-II12` |

### PENDIENTE de validar / decidir
- [ ] Pegar la fórmula en **CQ12**, arrastrar y confirmar **MA-0040 = 0.0**.
- [ ] Si cierra, replicar a los otros 11 meses (tabla de arriba).
- [ ] **A revisar (no decidido): CK aplica estacionalidad dos veces.** En la condición del
  IF compara `CJ12*CS$2*CV$2` contra el stock, pero **CJ12 ya trae** estacionalidad y
  evento. En MA-0040 no cambió el número (factor 0.88), pero en temporada alta (factor >1)
  puede topear mal la venta. Fix sugerido: sacar `*CS$2*CV$2` de la condición →
  `=ROUND(IF(CJ12>((IF(CO12<0;0;CO12))+CT12);(IF(CO12<0;0;CO12))+CT12;CJ12);0)`.

---

## Estructura del Forecast.xlsm (hoja "Forecast") — referencia

- Headers en fila 3, datos desde fila 6. Identidad: UN=A, GA=B, Código=C, Cat=F,
  Stock máx/Ideal=H, Caja x=L, Stock=BN, Meses=BO, Tendencia=AN, Precio Mix=AS.
- **Bloques mensuales:** inicio **CJ=col 88**, stride **14**. Septiembre = bloque 0.
- Offsets dentro de cada bloque (base = inicio del bloque):
  - `+1` Venta proy. unidades (CK) · `+4` Venta proy. USD/$ (CN) · `+5` Stock inicio (CO)
  - `+7` Meses fin de mes (CQ) · `+10` Cantidad confirmada / Compra (CT)
- Columnas del bloque Septiembre en detalle: CJ=V.Ajust c/stock (demanda), CK=Venta proy
  unid, CN=Venta proy USD/$, CO=Stock inicio, CP=Stock máximo, CQ=Meses, CR=Cantidad
  proyectada a comprar, CS=Total, CT=Cant confirmada, CU=Precio confirmado, CV=Total.
- **CJ (demanda)** = `ROUND(BV*(1+AN)^n * estac * evento; 0)`.
- **CK (venta)** = `min(demanda, stock disponible)`, con `IF(CO<0;0;CO)+CT` como disponible.
- **CO (stock inicio)** = `ROUNDUP(prev StockIni + prev Compra − prev VP)` (con OFFSET) =
  stock final del mes anterior.
- **CP (stock máximo)** = suma de la proyección de los próximos **H** meses (H = col H,
  "Stock máximo"/Meses máx), vía INDEX/MATCH sobre `AU:BH`.
- **CR (cantidad a comprar)** = `MROUND(MAX(0; MAX(CP;L)−CO−CT); L)`.
- **AU:BH** = proyección/demanda mensual **contigua** (Sept..Ago), meses en fila 3.
  Es la demanda cruda (≠ Venta proyectada topeada por stock).

## Archivos y flujo del dashboard
- Fuente: `Forecast.xlsm` (hojas "Forecast" + "Configuracion" [estacionalidad L/M/N] +
  ahora "V.R. mensual"), `Costos.xlsm` (hoja "General", en `...\Gestor de precios\Masters\`),
  y `Forecast MM-26.xlsm` congelados en subcarpeta `\Histórico\`. Cache: `historico_vp.json`.
- Editar SIEMPRE `generador/plantilla.html` (no el HTML final). Regenerar con
  `Subir_a_GitHub.bat`. GA "Adicionales" se excluye.

## Nota de entorno (por qué se hace este resumen)
El 14/09 no se pudo trabajar desde Cowork: una actualización de Windows (08/09) bloquea el
acceso del entorno de trabajo a los archivos. **Claude Code no está afectado** → seguir
desde ahí. (Pasó lo mismo con el dashboard Taller BV.)
