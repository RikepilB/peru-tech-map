# PeruGrid V1 + Cowork Scout: plan de recuperación e integración

Fecha: 2026-09-08. Estado: ejecución en curso; PG-04 preparado para revisión.

Actualización de ejecución: **PG-01–03, CS-01–03 e INT-01 están fusionados**. La corrección
PG-03.1 reemplazó el selector excluyente por controles combinables mediante el PR #47.
**DATA-01 está fusionado**: reconcilia sedes verificadas y deja los candidatos inciertos como
backlog editorial. PG-04 añade la vista pública Trabajar remoto; QA-01 continúa pendiente.

Ampliación solicitada: [rendimiento, lazy loading, caché y evaluación Astro/Next/Go](2026-09-08-performance.md).
PERF-00 mide la base antes de optimizar; PG-01 sigue como primera entrega de código.
QA-01 incorpora los gates PERF-01–03; cambios de framework quedan como evaluación condicionada.

## Objetivo y alcance

Resolver el backlog abierto de V1, terminar el flujo útil de Cowork Scout e integrar sus
resultados verificados en PeruGrid. Esta sesión entrega lectura, diagnóstico y planificación.
La aplicación continúa estática, con `index.html`, MapLibre y JSON; Scout continúa como
herramienta local Python/SQLite. No hacen falta Django, cuentas, API pública ni MCP para este
primer resultado. El roadmap V2 sigue vigente como trabajo posterior.

Resultado para el visitante: alternar Ecosistema / Trabajar remoto, elegir Lima o Arequipa,
filtrar tipos de lugar y consultar detalles fiables sin confundir popularidad con aptitud
para trabajar. Resultado para el mantenedor: investigar, revisar y preparar una actualización
repetible sin editar a mano registros ambiguos ni publicar automáticamente datos crudos.

## Línea base verificada

| Área | Evidencia actual | Implicación |
|---|---|---|
| PeruGrid | `origin/master` = `d7c9a6e`; PR #40 merged el 2026-07-25; ningún PR abierto | No repetir el arreglo de rendimiento ni pedir su merge |
| Checkout inicial | `fix/building-highlight-perf`; sin diferencias de contenido respecto a `origin/master` | Plan en nueva rama `codex/plan-perugrid-v1-scout` |
| Datos | 90 entidades, 16 titulares; campos actuales y bbox pasan; 90/90 tienen `tag_es` | Las cifras 75/89 de planes e issues están obsoletas |
| Taxonomía | 38 Startup, 11 Consultancy, 3 Acquired, 11 Incubator, 17 Coworking, 5 Nonprofit, 5 Fund | Cafés y bibliotecas comparten hoy Coworking; categoría y financiación están mezcladas |
| CI | Base pre-PG-01: JSON y presencia de campos; tras PG-01, `ci.yml` ejecuta `scripts/validate_data.py`, pruebas del validador y render seguro en Chromium | La base no cubría enums, tipos, duplicados ni URLs seguras; el validador actual cubre esquema, tipos, enums, bbox, duplicados y formato de enlaces; ninguna versión garantiza veracidad |
| Scout | `master`, commit local `d8deb1e`; no issues ni PRs abiertos consultados en GitHub | Su backlog debe derivarse del código y del diseño, no de checkboxes históricos |
| Pruebas Scout | `.venv/Scripts/python -m pytest -q`: **22 passed** | Base útil, pero no cubre los defectos reproducidos abajo |
| Configuración local | Ambos repos tienen definiciones de 11 agentes en `.codex/agents` y `.agents/agents` | Asignar responsabilidades concretas; no lanzar todos los agentes |

No se comprobó visualmente producción en esta sesión. No hubo llamadas reales a Places,
envíos FormSubmit, instalaciones, commits, pushes ni cambios en issues.

## Backlog GitHub reconciliado

| Issue | Estado / trabajo real | Cierre verificable |
|---|---|---|
| [#17](https://github.com/RikepilB/peru-tech-map/issues/17) | Abierto. Esquema y migración de **90** registros | Categoría explícita, etapa opcional solo Startup, validación y lectura compatible |
| [#19](https://github.com/RikepilB/peru-tech-map/issues/19) | Abierto, depende de #17 | Filtros Incubator / Accelerator / VC separados, etapas Startup, formulario y docs coherentes |
| [#11](https://github.com/RikepilB/peru-tech-map/issues/11) | Abierto, parcialmente incorporado | Cada candidato/sede termina añadido, rechazado con motivo o pendiente explícito; no duplicar existentes |
| [#12](https://github.com/RikepilB/peru-tech-map/issues/12) | Abierto; el handoff afirma verificaciones que el issue no refleja | Revalidar Tekton Labs, Netzun/Netzum, TuRuta y Juntoz; documentar exclusiones y sus fuentes |
| #8–10, #13–16, #18 | Cerrados en GitHub | Regresión focalizada cuando se toque su comportamiento; no reabrir por documentación vieja |
| #23–30 | Ocho issues V2 abiertos | Se mantienen separados; una vista estática remota no cierra #28, que requiere datos publicados del backend V2 |

En #11 ya existen Vallejo Librería-Café, La Bodega Verde, Sofá Café Barranco y Biblioteca
Municipal de Barranco. Confirmar si Café Sur y Cafetería de Consumo Mínimo son candidatos
distintos y vigentes; revisar Casatomada, Caleta Dolsa, Biblioteca San Isidro y sedes adicionales
de Regus/WeWork. Cada sucursal necesita identidad y coordenadas propias. No inventar precios.

En #12 conservar el criterio geográfico documentado para Hub UDEP, Phantasia, IMPAQTO Capital
y Wynwood House; no reinterpretar una inversión peruana como oficina física peruana.

## Hallazgos que condicionan el orden

| Prioridad | Hallazgo | Evidencia / estado |
|---|---|---|
| P0 | Datos externos interpolados en HTML y atributos — resuelto en PG-01 | Evidencia histórica pre-PG-01: `index.html:975/1062/1098` (ticker, popup, sidebar), hallazgo de código sin explotación en navegador; el render actual interpola vía `escapeHTML` con URLs validadas y pruebas DOM |
| P0 | Fuente Google no puede convertirse sin más en dataset público MapLibre | Restricciones actuales de Places sobre almacenamiento y mapas; ver contrato de fuentes |
| P1 | Scout no utiliza evidencia de amenities para puntuar | `scout/cli.py:33`: texto = nombre + dirección + web; `docs/USAGE.md` reconoce la limitación |
| P1 | Negaciones producen puntos positivos | Reproducción: `no wifi, no outlets, not quiet` devuelve 42.0; `sin wifi, sin enchufes` devuelve 17.5 |
| P1 | Se pierden páginas válidas si falla una posterior | MockTransport: página 1 válida + página 2 HTTP 503; `search_venues` lanza excepción y no devuelve resultados anteriores |
| P1 | Falta contrato geográfico y de publicación | `scout/db.py:6` sin coordenadas, fuentes ni estado; `places.py:17` asigna la ciudad solicitada, sin comprobar ubicación |
| P1 | Pins históricos de baja confianza | `docs/decisions.md` reconoce coordenadas genéricas en Talently/uDocz y baja confianza en Winnipeg Capital; registros siguen presentes. MindQube requiere revalidación de identidad |
| P2 | Reejecutar sin briefs borra conteo previo | `scout/cli.py:31`: escribe cero y recalcula todos los registros de la ciudad |
| P2 | Conteos y resultados parciales poco fiables | `cli.py:26` informa longitud recibida, aunque fallen upserts; una categoría puede contarse exitosa sin persistir un registro |
| P2 | Documentación de clave contradice ejecución | `docs/USAGE.md` propone `.env`; `scout/env.py` solo consulta variables de entorno |

Los hallazgos de código necesitan pruebas de regresión antes de arreglarse. El número de
tests actuales no prueba que el scoring sea útil ni que el producto esté listo para producción.

## Contrato de integración propuesto

```text
Fuentes permitidas / evidencia local estructurada
                  ↓
Scout: candidatos → resolución de sede → señales con evidencia
                  ↓
Revisión: coordenadas, fuentes, vigencia y permisos de publicación
                  ↓
Exportación JSON versionada + informe de rechazados + diff
                  ↓
PeruGrid: validación → dataset aprobado → vista Trabajar remoto
```

### Fuentes y permisos

La documentación de [Places](https://developers.google.com/maps/documentation/places/web-service/policies)
consultada el 2026-09-08 restringe almacenamiento salvo excepciones y establece Google Maps
para mostrar sus resultados en un mapa. Sus [términos específicos](https://cloud.google.com/maps-platform/terms/maps-service-terms)
deben revisarse para el contrato aplicable, incluyendo diferencias regionales.

**Decisión propuesta:** mantener el adaptador Google separado del exportador público.
No copiar sus ratings, reviews, coordenadas ni otros campos a `companies.json`, ni relabelar
datos derivados como propios. Una aprobación editorial no elimina restricciones de origen.
El camino público usa observaciones propias, datos aportados con permiso y otras fuentes
cuyos derechos y atribución sean compatibles. Un enlace web por sí solo no demuestra permiso.
La revisión del almacenamiento existente de Scout forma parte del trabajo, sin borrar bases
locales ni inspeccionar sus datos personales durante esta planificación.

Primera integración completamente verificable con fixtures sintéticos y un pequeño conjunto
independientemente investigado. Elegir un proveedor nuevo solo tras evaluar cobertura y
licencia; no agregar scraping, plugins ni APIs pagadas por inercia.

### Modelo mínimo

- **Organización:** entidad; **sede:** ubicación física concreta. Una marca puede tener varias.
- **Candidato:** registro aún no publicable. **Verificado:** identidad, posición y hechos
  respaldados. **Publicado:** subconjunto aprobado para el JSON público.
- `schema_version`, `id` estable de sede independiente de Google, `name`, `city` normalizada
  (`lima`, `arequipa`), `category`, `subcategory` opcional, `lat`, `lng`, dirección y web segura.
- `workspace_type`: `coworking`, `cafe`, `library`; restaurantes/hoteles quedan como candidatos
  de Scout hasta contar con un tipo público y criterio de aptitud definidos.
- Fuentes por campo/hecho: URL o referencia, fecha de observación, procedencia y condición
  de uso/atribución. Estado de revisión separado del score. Evidencia cruda privada fuera
  del paquete público; exportar solo referencias y hechos autorizados.
- Señales: `yes`, `no`, `unknown`, `conflicting`; fecha y evidencia específica del lugar.
  Desconocido no significa ausencia. Una mención popular no prueba Wi-Fi ni tolerancia a laptops.
- Score interno explicable y versionado; cobertura de evidencia separada. La primera vista
  pública omite el ranking numérico hasta pasar una evaluación manual de casos etiquetados.

### Migración y compatibilidad

Agregar `category` sin eliminar inmediatamente `funding`; lector transitorio prefiere el campo
nuevo. Verificar cada Fund antes de convertirlo a VC: una asociación no se vuelve fondo.
Acquired es un estado de organización, no una etapa; preservar ese dato y revisar su categoría.
No asignar Bootstrap ni otra etapa por falta de información. Cafés y bibliotecas conservan
identidad y ganan `workspace_type`; no duplicar los 17 lugares existentes al importar.

Propuesta inicial: paquete de intercambio separado, importador con dry-run y aprobación local
que actualiza el mismo `companies.json`. Evita dos datasets públicos incompatibles para la
misma sede. El importador valida el esquema real de PeruGrid, no una copia privada divergente.
La segunda importación idéntica debe generar cero cambios; conflictos de sede quedan pendientes.
Registros remotos o sin coordenadas válidas permanecen candidatos, sin pin de centro de ciudad.

## Secuencia de implementación

Cada fila produce una entrega comprobable. Estimaciones relativas: S pequeña, M media,
L dividir en varias sesiones. No representan fechas comprometidas.

| ID | Entrega / archivos principales | Depende de | Aceptación | Tamaño |
|---|---|---|---|---|
| PG-01 | Render seguro y validador ejecutable: `index.html`, `tests/`, `.github/workflows/ci.yml` | — | HTML en nombre/tag/ticker se muestra literal; URLs fuera del formato permitido rechazadas; 90 registros válidos; esquema, bbox, enums y duplicados negativos cubiertos | M |
| PG-02 | Taxonomía compatible: dataset, lector, documentación y formulario; #17 | PG-01 | Categorías no mezcladas con financiación; etapas solo si respaldadas; todos los registros conservados o enviados a revisión con razón | M |
| PG-03 | Filtros utilizables: `viewState`, `typeVisible`, sidebar, ES/EN; #19 | PG-02 | Incubator/Accelerator/VC separados; categorías y etapas coherentes; city + filtro + vacío + popup funcionan en móvil y escritorio | M |
| CS-01 | Contrato de candidatos y fuentes; DB con migración versionada; importación local sintética | — | ID/sede, coordenadas, procedencia y estado persistidos; migración conserva datos; paquete Google rechazado para publicación | M |
| CS-02 | Scoring basado en evidencia atribuible: `mentions.py`, `score.py`, `weights.py`, `cli.py` | CS-01 | Positivos/negativos ES/EN, desconocido y contradicción diferenciados; sin contaminación entre sedes ni duplicación de citas; rerun sin briefs conserva evidencia | M |
| CS-03 | Ejecución parcial fiable: adaptadores, CLI, DB | CS-01 | Fallo en página 2 conserva página 1; informes distinguen recibido/persistido/rechazado; CLI informa parcial vs fallo total; límites de páginas/solicitudes y reintentos acotados | M |
| INT-01 | Un lugar sintético recorre Scout → exportación → dry-run → PeruGrid | PG-02, CS-01–03 | Contrato compartido real; coordenadas/city/URL inválidos y origen restringido rechazados; importación idempotente; ninguna credencial llega al navegador | M |
| DATA-01 | Reconciliar candidatos y sedes; #11 y #12; revisar pins de baja confianza | CS-01, PG-02 | Matriz por candidato con fuente/fecha/decisión; sin deduplicación por marca; ninguna coordenada inventada | L |
| PG-04 | Vista integrada Trabajar remoto | PG-03, INT-01 | Alternar modos y ciudad; tipos coworking/cafe/library; lugares sin evidencia no anuncian amenities; detalles con fuente/fecha; estilo Costa Verde existente | M |
| QA-01 | Cierre V1 + Scout: regresión, documentación y paquete revisable | Todo lo anterior | Suite, contrato, browser, rendimiento y limitaciones documentados; issues reconciliados en borrador local | M |

Para PG-02, trabajar primero sobre fixtures representativos (startup con/sin etapa,
adquirida, fondo/asociación, café, biblioteca), luego aplicar a las 90 entradas. INT-01 usa
una sede sintética completa antes de ampliar DATA-01. No esperar una investigación de ciudad
entera para demostrar la integración.

Para CS-02, evaluar antes de ajustar pesos: al menos 12 casos revisados que cubran negación,
idiomas, homónimos, sucursales, citas repetidas y evidencia ausente/contradictoria. Criterio
mínimo: cero amenities positivos inventados en esos casos y explicación del score reproducible.
No añadir Places Details como solución automática: añade coste y restricciones de contenido.

## Verificación y definición de terminado

1. **Scout offline:** conservar los 22 tests y agregar regresiones conductuales de los
   hallazgos; mockear fuentes, no SQLite ni el exportador en la prueba integral.
2. **Datos:** un único validador reutilizado por CI e importador; tipos estrictos, números
   finitos, bbox, city, enums, condiciones, ID/sucursal, enlaces y trazabilidad.
3. **Contrato:** fixture generado por Scout aceptado por el consumidor real PeruGrid;
   versión desconocida, fuentes restringidas y estados no aprobados fallan sin modificar destino.
4. **Navegador:** HTTP local; Lima/Arequipa; ES/EN; filtros; modos; popup; selección;
   vacíos y fallos de JSON; teclado/foco; móvil; prueba del formulario interceptada sin envío.
5. **Rendimiento:** interacción repetida y cambios de filtros/ciudad; medir listeners,
   marcadores y consultas de edificios. Comparar con la base PR #40 bajo el mismo entorno;
   no declarar estabilidad solo por leer código o por un navegador con tiles congelados.
6. **Fuentes reales:** muestra pequeña con permisos/coste actuales antes de ampliar. Los tests
   offline no prueban conectividad, cuota ni cobertura comercial. Registrar la muestra real
   por separado si se autoriza y ejecuta.
7. **Entrega:** diff revisado, documentación fiel, comandos/resultados y limitaciones;
   commit/push/PR/deploy/cierre de issues únicamente cuando se soliciten. Verificación local
   no equivale a despliegue. #11/#12 con candidatos irresueltos no se declaran cerrados.

## Recursos revisados después del primer borrador

Se inspeccionaron selectivamente las dos colecciones locales de Nelson Lee y los directorios
de skills indicados. No se leyeron todos los artículos ni se instalaron skills.

| Recurso | Idea incorporada | Aplicación concreta |
|---|---|---|
| Nelson: From Spec to Backlog | Especificación antes del backlog; dependencias explícitas | Tabla PG/CS/INT con criterios; borrador local antes de publicar tickets |
| Nelson: Security Checklist (nota del vault + archivo de posts) | Evidencia por hallazgo; UNKNOWN cuando falta comprobación | Render inseguro y frontera de fuentes antes de ampliar ingestión; no simular auditoría de auth inexistente |
| Nelson: Boris Cherny Four Routines (ambas colecciones) | Tests sobre resultados costosos; evitar rituales y abstracciones innecesarias | Regresiones de scoring/persistencia/contrato, sin objetivo artificial de cobertura ni automatizaciones nuevas |
| Nelson: 16 Things Before Launch | Separar comprobación visual de inferencia | Browser, metadatos, enlaces, formulario y estado de producción en QA |
| Matt Pocock: to-spec / to-tickets | Especificación y unidades pequeñas con bloqueos; expandir antes de retirar | Migración compatible y una sede completa como primera integración; sin ejecutar publicación automática de los skills |
| Matt Pocock: domain-modeling | Nombres de dominio precisos | Organización/sede/candidato/publicado; señales distintas de popularidad |
| skills-lab: grill-with-docs | Leer decisiones antes de preguntar | Supuestos reversibles explícitos; no reiniciar entrevistas sobre stack ya documentado |
| skills-lab: debug-evidence-loop | Reproducir antes de editar | Negaciones y pérdida de página reproducidas sin red |

Para la implementación visual: aplicar `design-intent` y `anti-slop-review` sobre el contrato
Costa Verde existente. `landing-audit` y `production-readiness` antes de un lanzamiento.
`disposable-prototype` solo si una duda concreta de interacción necesita demostración.
No se justifica instalar un nuevo conjunto de herramientas ni activar skills globales.

## Uso propuesto de los agentes instalados

- **planner:** preparar una entrega acotada y sus criterios; **architect:** revisar el contrato
  Scout/PeruGrid y la transición de categorías una sola vez.
- **tdd-guide / test-writer:** regresiones de señales, persistencia e importación;
  **security-reviewer:** HTML/URLs y separación de datos públicos/privados.
- **code-reviewer:** revisar el diff integrado; **e2e-runner:** journeys y rendimiento;
  **doc-updater:** documentación y handoff después de la verificación.
- `database-reviewer` se especializa en PostgreSQL: no asignarle SQLite automáticamente.
  `build-error-resolver` solo ante un fallo real; V1 no tiene compilación TypeScript.
  `refactor-cleaner` no necesita una barrida general para este alcance.

La paralelización útil, si se ejecuta con subagentes, es PG-01 frente a CS-01; luego las
entregas de cada repo según dependencias. Un único responsable edita `index.html` y otro
`companies.json`; revisar juntos antes de integrar. Los agentes no deben revertir cambios
ajenos. Esta sesión inspeccionó las definiciones, no ejecutó subagentes.

## Estado de ejecución y siguiente acción

PG-01, PG-02 y PG-03 están fusionados en `master` mediante los PR #41, #42 y #44; la corrección
responsive/táctil mediante el PR #43 y los filtros combinables mediante el PR #47. En Coworking
Scout, CS-01, CS-02 y CS-03 están fusionados mediante los PR #2, #3 y #4. INT-01 está fusionado
en ambos repositorios (Scout #5–6 y PeruGrid #46). DATA-01 aplica la matriz
`docs/data-reconciliation-2026-09-09.md`, sustituye pins genéricos por ocho sedes trazables y
mantiene los casos sin coordenada exacta como pendientes. PG-04 implementa la vista pública
«Trabajar remoto» con tipos combinables y solo publica lugares respaldados por una fuente pública
redistribuible. El siguiente frente es QA-01 y la línea base de rendimiento. Conservar en ambos
repositorios los archivos locales ajenos.

## PG-03.1 — Corrección UX del selector de filtros

Decisión tomada a partir de la captura del sidebar en escritorio del 2026-09-08. La persona
que explora el ecosistema necesita elegir ciudad y una vista útil en pocos segundos, y después
abrir una empresa o lugar. La captura muestra nueve pills del mismo peso visual, agrupadas por
labels débiles y con un reset implícito; el estado y la relación categoría-etapa no se entienden.

Dirección: conservar el lenguaje visual Costa Verde y el panel compacto, pero convertir los
filtros en un formulario jerárquico. Ciudad y orden permanecen como controles segmentados. Un
selector de ancho completo, «Qué quieres ver», incluye una opción inicial explícita «Empresas»
(startups + consultoras) y cada categoría pública, incluidas Startup y Consultora. «Etapa de
startup» aparece solo al elegir Startup, con «Todas las etapas» y las cuatro etapas válidas. Un
botón textual «Limpiar filtros» aparece únicamente fuera de la vista inicial.

No se agregan iconos decorativos, accordions ni un nuevo sistema visual. Los controles nativos
mantienen teclado, foco y lectura de estado; en móvil ocupan el ancho disponible y respetan 44 px
de altura. La ciudad seleccionada persiste al cambiar vista o etapa. Elegir otra categoría limpia
la etapa oculta; limpiar restaura Empresas sin cambiar ciudad ni orden.

Verificación: escritorio 1280×800 y móvil 390×844; selección con teclado; ES/EN; todas las
categorías; Startup con y sin etapa; reset; estado vacío; selección de fila y popup. La revisión
visual debe comprobar jerarquía, wrapping, contraste y área táctil sobre una página servida por
HTTP.

Veredicto anti-slop: **PASS**. La inspección servida por HTTP en 1280×800 y 390×844 confirma que
el bloque jerárquico de `index.html:520` reemplaza nueve acciones del mismo peso por una primera
decisión explícita, revela la etapa solo cuando aporta contexto y mantiene el reset junto a los
controles. En móvil, los selects de `index.html:456` ocupan el ancho disponible y miden 44 px; no
hay wrapping, solapamiento ni un sistema visual nuevo. Se conservan ciudad y orden como controles
segmentados, el verde Costa Verde para estados activos y los controles nativos. Las pruebas de
Chromium vuelven a comprobar teclado, ES/EN, todas las categorías, estado vacío, popup, reset y
las vistas móvil y escritorio.
