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

Cuando el usuario diga **"actualizar forecast"** (o publicar/regenerar el dashboard),
seguir la skill `forecast-dashboard`, que se carga sola al abrir esta carpeta.

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

Los dos Excel fuente están en Drive:

- `G:\Unidades compartidas\7. Compras y producto\7.3. Compras\7.3.3. Rotación\Forecast\Forecast.xlsm`
- `G:\Unidades compartidas\7. Compras y producto\7.4. Producto\7.4.5. Gestor de precios\Masters\Costos.xlsm`

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
