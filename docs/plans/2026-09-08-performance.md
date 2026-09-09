# Rendimiento de PeruGrid y Cowork Scout

Estado: PERF-00 ejecutado el 2026-09-09; PERF-01 es el siguiente frente. Complementa
[V1 + Scout](2026-09-08-v1-cowork-scout.md). La evaluación conserva la aplicación estática;
Astro, React/Next.js y Go continúan condicionados a una necesidad y comparación medible.

## Recomendación

Optimizar primero el recorrido actual HTML/JavaScript + MapLibre, y Python/SQLite en Scout.
Medir carga, interacción, trabajo repetido y ejecución de Scout por separado. Considerar
Astro cuando existan páginas de ciudades, sedes o guías que se beneficien de generación estática.
No atribuir una mejora de velocidad a un framework o lenguaje sin comparar el mismo trabajo.

## Evidencia del código y del servicio actual

- Archivos locales sin comprimir tras PG-04: `index.html` 96.019 bytes; `companies.json` 53.624;
  `ticker.json` 2.037. El dataset tiene 89 entradas: dividirlo ya añade complejidad para
  ahorrar una carga pequeña. No se midió el peso total de MapLibre, tiles, fuentes ni logos.
- `index.html:650`: las peticiones de empresas y ticker comienzan dentro de `map.on("load")`.
  La descarga de datos puede solaparse con la inicialización del mapa.
- `index.html:941`: cambiar ciudad/filtro elimina todos los marcadores y reconstruye lista
  y marcadores. Hipótesis de coste evitable; no hay perfil de CPU de navegador todavía.
- `index.html:663` y `index.html:866`: idle programa el cálculo de edificios y este hace
  `setData()` sin comparar resultados. Verificar si ese cambio genera sucesivos ciclos idle;
  no está demostrada una fuga o un bucle en esta sesión.
- El arreglo #40 ya limita consultas nativas por capa y usa requestAnimationFrame para hover.
  Su búsqueda geométrica restante recorre empresas visibles × edificios visibles: medir
  antes de introducir un índice espacial.
- Sidebar ya usa imágenes `loading="lazy"`, con dimensiones y decoding async (`index.html:1098`).
  La carga de MapLibre ya usa defer (`index.html:190`); defer no equivale a cargar bajo demanda.
- Lectura HTTP real de `/`, `/companies.json` y `/ticker.json`: 200, Brotli, ETag y
  `Cache-Control: public, max-age=0, must-revalidate`. La página dio X-Vercel-Cache HIT.
  Una primera petición JSON dio MISS; otra dio HIT. `If-None-Match` del dataset devolvió 304.
  Por tanto ya existe caché CDN y revalidación; no hay evidencia de que esté desactivada.
- `fetch(..., {cache:"no-cache"})` permite almacenamiento pero obliga a revalidar. No es
  `no-store`. Cambiarlo requiere primero definir cuánto tiempo puede permanecer viejo el dato.
- Scout ejecuta categorías secuencialmente; cada upsert, actualización de menciones y score
  hace commit. `mentions.py` vuelve a separar/minusculizar el corpus para cada lugar.
  Son oportunidades observadas, no porcentajes de mejora medidos.

## Tecnologías: utilidad y condición de adopción

| Opción | Qué aporta aquí | Recomendación |
|---|---|---|
| HTML/JS actual | Sin hidratación de un framework; despliegue estático ya funcional | Base para cerrar V1 y medir mejoras |
| Astro estático | Componentes, rutas y páginas HTML de ciudades/sedes; JS selectivo para interactividad | Mejor candidato si crece el contenido. Puede usar MapLibre con JS normal, sin React |
| React | Modelo de componentes y estado compartido para interfaces complejas | No introducirlo solo por velocidad; no elimina el trabajo WebGL ni los tiles |
| Next.js | Framework React con capacidades de servidor y carga diferida | Evaluar si aparecen requisitos reales de servidor; no reemplazar silenciosamente el roadmap Django |
| Go | Opción para un servicio o tarea CPU-bound medida, y distribución como binario | Mantener Python hasta identificar una función cuyo coste justifique portar y mantener otro runtime |

Astro renderiza HTML estático e hidrata componentes seleccionados; Next permite lazy loading
de componentes cliente/librerías. Ninguno reduce por sí mismo el trabajo del mapa.
Referencias: [Astro islands](https://docs.astro.build/en/concepts/islands/),
[Next lazy loading](https://nextjs.org/docs/app/guides/lazy-loading),
[Go diagnostics](https://go.dev/doc/diagnostics).
Esto es una evaluación de encaje, no un benchmark entre frameworks.

## Carga y renderizado de PeruGrid

1. Iniciar la petición única del dataset mientras carga MapLibre. Separar datos disponibles
   de mapa listo; renderizar la lista antes si es viable y deshabilitar temporalmente acciones
   que requieren mapa. Evitar peticiones duplicadas y manejar fallos de cada recurso.
2. Mantener el mapa principal prioritario: cargarlo al hacer scroll o clic retrasaría el
   propósito central de esta página. En futuras guías con un mapa secundario sí cargarlo
   al entrar en viewport. Diferir ticker y detalles secundarios sin bloquear la primera lista.
3. Comparar geometrías/identificadores antes de actualizar fuentes de edificios. Invalidar
   por datos, viewport y cambios relevantes de tiles/estilo; un simple cache por zoom sería
   incorrecto. Confirmar que un mapa quieto deja de recalcular tras estabilizarse.
4. Evaluar reconciliación por ID estable de sede en vez de destruir todos los elementos.
   Conservar selección correcta y liberar listeners/elementos retirados. Un solo popup activo.
5. Medir blur, antialias y animación inicial; ofrecer menor movimiento y coste visual cuando
   corresponda. No reducir legibilidad ni ocultar carga fallida para mejorar métricas.
6. Si los marcadores DOM dominan el perfil, comparar GeoJSON + capas circle/symbol y clusters
   con el diseño actual. Mantener logos/detalle del seleccionado y accesibilidad de la lista.
   Virtualizar la lista solo al superar el presupuesto de interacción, no por tener 90 registros.
7. Particionar por ciudad cuando el tamaño/tiempo de descarga lo justifique. Vector tiles,
   simplificación y carga espacial son escalones posteriores, no requisitos iniciales.

[Guía oficial de rendimiento MapLibre](https://maplibre.org/maplibre-gl-js/docs/guides/large-data/).
Compatibilidad de cualquier API nueva debe verificarse con la versión 4.7.1 actualmente usada;
la documentación actual no autoriza una actualización implícita.

## Contrato de caché propuesto

| Recurso | Política inicial propuesta | Invalidación / comprobación |
|---|---|---|
| HTML y JSON mutable actuales | Conservar revalidación ETag como primera mejora segura | Publicar versión nueva y comprobar cuerpo/ETag; 304 si no cambia |
| Assets propios con hash en nombre | `public, max-age=31536000, immutable` | Cambio de contenido exige URL nueva; nunca aplicar a `index.html` o `companies.json` estables |
| Dataset público versionado, fase posterior | Manifest pequeño revalidado → snapshot `companies.<hash>.json` inmutable | Publicación atómica de manifest+snapshot; conservar versión anterior durante transición/rollback |
| Ticker mutable | Evaluar browser max-age=60, CDN s-maxage=300, stale-while-revalidate=60 | Aceptación explícita de retraso de hasta unos minutos; probar comportamiento real de hosting |
| Datos en memoria de página | Una promesa de fetch compartida + índices derivados por versión/ciudad | Desechar al cambiar versión; acotar caché y evitar conservar DOM retirado |
| Fuentes/tiles/logos de terceros | Respetar política del proveedor | No prometer TTL controlado por PeruGrid ni crear proxy masivo de tiles |
| Evidencia/score de Scout | Clave por sede + hash de evidencia + versión de algoritmo/pesos + reglas de normalización | Recalcular solo si cambian entradas; vencimiento de evidencia puede retirar publicación |

Para caché de fuentes de Scout, incluir proveedor, versión de adaptador, consulta normalizada,
ubicación y parámetros relevantes. Nunca incluir secretos en claves persistidas/logs. Guardar
fecha, expiración y permisos; cache miss/error no debe convertirse en evidencia positiva.
Aplicar restricciones del proveedor antes que un TTL genérico: el contenido Places no adquiere
permiso de almacenamiento/publicación por guardarlo en una caché privada.

No introducir Redis ni service worker ahora. Hay CDN/browser cache y SQLite suficientes para
probar este flujo. Offline/PWA requiere un contrato propio de expiración y actualización.
Mantener retiro de datos incompatible con cualquier ventana de caché: registros sensibles a
retiro urgente requieren revalidación/purga y nunca la política relajada del ticker.

Referencias: [HTTP caching](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching),
[Vercel Cache-Control](https://vercel.com/docs/caching/cache-control-headers).
Verificar headers en un despliegue autorizado: editar configuración local no prueba caché CDN.

## Optimización de Scout conservando Python

- Medir tiempo por red, parseo, resolución, scoring y SQLite; contar peticiones y commits.
- Reutilizar el cliente HTTP y procesar páginas por lotes; persistir cada página exitosa.
  Agrupar escrituras dentro de una transacción por lote y guardar progreso antes de pedir
  otra página. Un error de registro usa aislamiento apropiado sin perder el lote válido.
- Normalizar y dividir corpus una vez; después asociar evidencia a sede y reutilizarla.
  Índices por tokens pueden reducir comparaciones, pero deben mantener recall en homónimos,
  abreviaturas y variaciones ES/EN; comparar con un conjunto etiquetado.
- Recalcular solo entradas cambiadas. No resetear menciones al omitir briefs; mantener la
  semántica de evidencia ausente, negativa y vencida.
- Concurrencia acotada de peticiones independientes solo después de medir cuotas, coste y
  rate limits; páginas con nextPageToken siguen dependientes. Empezar secuencial con checkpoints,
  luego comparar un límite pequeño configurable; un único escritor SQLite.
- No aumentar paralelismo, pagar APIs ni reescribir en Go para ocultar espera de red.
  Si CPU domina tras estas mejoras, comparar únicamente el componente crítico y medir
  sobrecarga de integración/distribución antes de decidir.

[Control de transacciones Python/SQLite](https://docs.python.org/3/library/sqlite3.html#transaction-control).

## Entregas añadidas y medición

| ID | Trabajo | Dependencias | Gate |
|---|---|---|---|
| PERF-00 | Línea base repetible de navegador y Scout | — | Perfiles, entorno, dataset y trazas guardados; distinguir cold/warm cache |
| PERF-01 | Solapar carga de datos y evitar trabajo de edificios sin cambios | PERF-00, PG-01 | Lista disponible antes; mapa estable sin actualizaciones propias repetitivas; regresiones funcionales pasan |
| PERF-02 | Caché pública e invalidación comprobable | PERF-00; contrato INT-01 para snapshots | 304/reutilización y versión nueva/rollback correctos; retiros respetados; headers reales comprobados al desplegar |
| PERF-03 | Lotes SQLite y procesamiento incremental | CS-01–03, PERF-00 | Mismos resultados correctos; menos commits/recomputación; interrupción conserva páginas previas |
| PERF-04 | Experimento de escala: DOM frente a capas/cluster y lista limitada | PG-04, PERF-01 | Aceptar solo si mejora en el mismo dispositivo sin perder interacción/accesibilidad |

PERF-00 precede cambios de rendimiento; PG-01 de seguridad sigue siendo la primera entrega
de código. PERF-01 se coordina con quien edita `index.html`; no abrir ediciones competidoras.
QA-01 incluye PERF-01–03; PERF-04 y un posible prototipo Astro quedan condicionados a evidencia.

Protocolo: al menos cinco repeticiones por escenario, mismo navegador/dispositivo, red y
dataset; registrar mediana y dispersión, no escoger la mejor captura. Escenarios: carga fría,
recarga caliente, ciudad/filtros/modos, 2D/3D, zoom/pan y diez minutos de interacción.
Fixtures sintéticos de 90, 1.000 y 10.000 lugares exploran límites sin adquirir datos reales.
Medir bytes transferidos, peticiones, primera lista útil, mapa interactivo, tareas largas,
latencia de filtros, memoria retenida, marcadores/listeners y consultas/actualizaciones de fuentes.

Presupuestos propuestos, pendientes de línea base: respuesta de filtros p95 ≤100 ms con el
dataset objetivo; cero crecimiento sostenido de objetos retenidos después de ciclos equivalentes;
ningún bucle de `setData` con viewport/datos estables. En Scout, rerun sin cambios evita scoring
repetido; duplicar entrada no implica duplicar llamadas a fuentes dentro de TTL permitido.
Para 1.000/10.000 registros, p95 y memoria determinan cuándo adoptar PERF-04; no se promete
ese rendimiento antes de medir.

PERF-00 guarda cinco pares fríos/calientes y muestras de interacción en
`docs/performance/perf00-browser-baseline-2026-09-09.json`. La primera lista útil, medida después
de dos frames, tuvo mediana 344,1 ms en frío y 353,7 ms en caliente bajo un retraso determinista
de mapa de 200 ms. Los filtros quedaron cerca o por debajo de 10 ms de handler. CDP registra la
navegación, JSON, status y bytes; la recarga local devolvió respuestas 200 completas sin hits de
caché. Cinco estados `idle` equivalentes repitieron diez escrituras GeoJSON; este es el objetivo
comprobable de PERF-01. Estas cifras no incluyen WebGL, tiles ni red pública y solo se comparan
en el mismo host/protocolo. Un trace diagnóstico separado acompaña la captura y CI conserva un
trace smoke durante 14 días.
